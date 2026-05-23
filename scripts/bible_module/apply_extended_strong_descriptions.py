from __future__ import annotations

import argparse
import json
import re
import shutil
import sqlite3
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from scripts.content_tool.helpers import GREEK_DESC_GROUP_RANGES

from .apply_extended_strong_entries import (
    CLASSIC_GREEK_STRONG_MAX,
    EXPECTED_ATTESTED_EXTENDED_COUNT,
    EXPECTED_PRIMARY_ATTESTED_EXTENDED_COUNT,
    UNUSED_EXTENDED_SENTINEL,
    build_attested_extended_strong_rows,
    load_lexicon_index,
)
from .schema import (
    DB_METADATA_DATA_VERSION_KEY,
    DB_METADATA_DATE_KEY,
    now_utc_iso,
)
from .sources import DEFAULT_SOURCE_LOCK_PATH

DEFAULT_DB_DIR = Path.home() / "Documents" / "revelation" / "db"
DEFAULT_COMMON_DB_PATH = DEFAULT_DB_DIR / "revelation.sqlite"
DEFAULT_BIBLE_MODULE_PATH = DEFAULT_DB_DIR / "bible_na28_lxx.sqlite"
SUPPORTED_LOCALES = ("en", "es", "ru", "uk")

LOCALIZED_EXTENDED_STRONG_DESCRIPTIONS: dict[int, dict[str, str]] = {
    6000: {
        "en": "to announce or report",
        "es": "anunciar o comunicar",
        "ru": "возвещать или сообщать",
        "uk": "сповіщати або повідомляти",
    },
    6001: {
        "en": "a vessel or container",
        "es": "vasija o recipiente",
        "ru": "сосуд или вместилище",
        "uk": "посудина або вмістилище",
    },
    6002: {
        "en": "Admin, a personal name in Luke's genealogy",
        "es": "Admin, nombre personal en la genealogía de Lucas",
        "ru": "Админ, личное имя в родословии Луки",
        "uk": "Адмін, особове ім'я в родоводі Луки",
    },
    6003: {
        "en": "to gather or assemble",
        "es": "reunir o juntar",
        "ru": "собирать или созывать",
        "uk": "збирати або скликати",
    },
    6005: {
        "en": "to dress or clothe",
        "es": "vestir o cubrir con ropa",
        "ru": "одевать или облачать",
        "uk": "одягати або вбирати",
    },
    6006: {
        "en": "to cast around or throw around",
        "es": "echar alrededor o envolver",
        "ru": "накидывать или бросать вокруг",
        "uk": "накидувати або кидати навколо",
    },
    6007: {
        "en": "amomum, a fragrant spice plant",
        "es": "amomo, planta aromática usada como especia",
        "ru": "амом, ароматическое пряное растение",
        "uk": "амом, ароматична пряна рослина",
    },
    6008: {
        "en": "to leap up or jump up",
        "es": "saltar o levantarse de un salto",
        "ru": "вскакивать или подпрыгивать",
        "uk": "підскакувати або схоплюватися",
    },
    6011: {
        "en": "a needle",
        "es": "aguja",
        "ru": "игла",
        "uk": "голка",
    },
    6013: {
        "en": "produce, fruit, or harvest",
        "es": "producto, fruto o cosecha",
        "ru": "плод, урожай или произведенное",
        "uk": "плід, урожай або вирощене",
    },
    6015: {
        "en": "fear, awe, or reverence",
        "es": "temor, sobrecogimiento o reverencia",
        "ru": "страх, трепет или благоговение",
        "uk": "страх, трепет або благоговіння",
    },
    6016: {
        "en": "to cleanse thoroughly",
        "es": "limpiar por completo",
        "ru": "тщательно очищать",
        "uk": "ретельно очищати",
    },
    6017: {
        "en": "to mock or deride",
        "es": "burlarse o mofarse",
        "ru": "насмехаться или глумиться",
        "uk": "насміхатися або глузувати",
    },
    6018: {
        "en": "to consider, reflect, or ponder",
        "es": "considerar, reflexionar o meditar",
        "ru": "обдумывать, размышлять или рассуждать",
        "uk": "обдумувати, розмірковувати або міркувати",
    },
    6019: {
        "en": "twenty thousand; twice ten thousand",
        "es": "veinte mil; dos veces diez mil",
        "ru": "двадцать тысяч; дважды десять тысяч",
        "uk": "двадцять тисяч; двічі по десять тисяч",
    },
    6020: {
        "en": "testing, proof, or examination",
        "es": "prueba, comprobación o examen",
        "ru": "испытание, проверка или исследование",
        "uk": "випробування, перевірка або дослідження",
    },
    6022: {
        "en": "to speak ill of or defame",
        "es": "hablar mal o difamar",
        "ru": "злословить или порочить",
        "uk": "лихословити або ганьбити",
    },
    6027: {
        "en": "questioning, dispute, or speculation",
        "es": "cuestionamiento, disputa o especulación",
        "ru": "спорный вопрос, прение или рассуждение",
        "uk": "спірне питання, суперечка або міркування",
    },
    6028: {
        "en": "to be greatly amazed",
        "es": "asombrarse profundamente",
        "ru": "сильно изумляться",
        "uk": "сильно дивуватися",
    },
    6029: {
        "en": "more exceedingly",
        "es": "aún más extraordinariamente",
        "ru": "еще более чрезвычайно",
        "uk": "ще надзвичайніше",
    },
    6030: {
        "en": "to spring out or rush out",
        "es": "salir de un salto o precipitarse fuera",
        "ru": "выскакивать или стремительно выбегать",
        "uk": "вискакувати або стрімко вибігати",
    },
    6031: {
        "en": "rebuke or reproof",
        "es": "reprensión o reproche",
        "ru": "обличение или упрек",
        "uk": "докір або викриття",
    },
    6032: {
        "en": "mockery or derision",
        "es": "burla o escarnio",
        "ru": "насмешка или издевательство",
        "uk": "насмішка або глузування",
    },
    6033: {
        "en": "from there, thence, or hence",
        "es": "desde allí, de allí o por eso",
        "ru": "оттуда, отсюда или поэтому",
        "uk": "звідти, звідси або тому",
    },
    6034: {
        "en": "to adjure or put under oath",
        "es": "conjurar o poner bajo juramento",
        "ru": "заклинать или обязывать клятвой",
        "uk": "заклинати або зобов'язувати клятвою",
    },
    6035: {
        "en": "accursed or under a curse",
        "es": "maldito o bajo maldición",
        "ru": "проклятый или находящийся под проклятием",
        "uk": "проклятий або той, що перебуває під прокляттям",
    },
    6036: {
        "en": "to come in upon or enter in",
        "es": "entrar sobre alguien o entrar dentro",
        "ru": "входить внутрь или внезапно наступать",
        "uk": "входити всередину або раптово наставати",
    },
    6037: {
        "en": "to sow upon or among",
        "es": "sembrar sobre o entre",
        "ru": "сеять поверх или среди",
        "uk": "сіяти поверх або серед",
    },
    6041: {
        "en": "to envy, be jealous, or be zealous",
        "es": "envidiar, tener celos o mostrar celo",
        "ru": "завидовать, ревновать или проявлять рвение",
        "uk": "заздрити, ревнувати або виявляти ревність",
    },
    6043: {
        "en": "Joda, a personal name in Luke's genealogy",
        "es": "Joda, nombre personal en la genealogía de Lucas",
        "ru": "Иода, личное имя в родословии Луки",
        "uk": "Йода, особове ім'я в родоводі Луки",
    },
    6044: {
        "en": "Josech, a personal name in Luke's genealogy",
        "es": "Josec, nombre personal en la genealogía de Lucas",
        "ru": "Иосех, личное имя в родословии Луки",
        "uk": "Йосех, особове ім'я в родоводі Луки",
    },
    6045: {
        "en": "just as or even as",
        "es": "tal como o así como",
        "ru": "точно так же как или подобно тому как",
        "uk": "точно так само як або подібно до того як",
    },
    6046: {
        "en": "to weigh down or burden",
        "es": "agobiar o cargar con peso",
        "ru": "отягощать или обременять",
        "uk": "обтяжувати або обтяжувати тягарем",
    },
    6048: {
        "en": "sentence, judgment, or condemnation",
        "es": "sentencia, juicio o condena",
        "ru": "приговор, суд или осуждение",
        "uk": "вирок, суд або осуд",
    },
    6049: {
        "en": "to bend down or stoop",
        "es": "inclinarse o agacharse",
        "ru": "наклоняться или пригибаться",
        "uk": "нахилятися або пригинатися",
    },
    6050: {
        "en": "to bless fervently",
        "es": "bendecir fervientemente",
        "ru": "усердно благословлять",
        "uk": "ревно благословляти",
    },
    6051: {
        "en": "an accuser",
        "es": "acusador",
        "ru": "обвинитель",
        "uk": "обвинувач",
    },
    6052: {
        "en": "to settle, establish, or colonize",
        "es": "asentar, establecer o colonizar",
        "ru": "поселять, утверждать или основывать колонию",
        "uk": "поселяти, утверджувати або засновувати колонію",
    },
    6053: {
        "en": "lower or further down",
        "es": "más bajo o más abajo",
        "ru": "ниже или дальше вниз",
        "uk": "нижче або далі вниз",
    },
    6055: {
        "en": "a small couch or cot",
        "es": "lecho pequeño o camilla",
        "ru": "небольшая постель или ложе",
        "uk": "невелике ложе або ноші",
    },
    6058: {
        "en": "hidden or secret",
        "es": "oculto o secreto",
        "ru": "скрытый или тайный",
        "uk": "прихований або таємний",
    },
    6059: {
        "en": "to encircle or surround",
        "es": "rodear o cercar",
        "ru": "окружать или обступать",
        "uk": "оточувати або обступати",
    },
    6060: {
        "en": "to turn around or change",
        "es": "volver o cambiar",
        "ru": "поворачивать или изменять",
        "uk": "повертати або змінювати",
    },
    6061: {
        "en": "made of millstone or millstone-like",
        "es": "hecho de piedra de molino o semejante a ella",
        "ru": "сделанный из жернова или подобный жернову",
        "uk": "зроблений із жорна або подібний до жорна",
    },
    6063: {
        "en": "to know",
        "es": "saber o conocer",
        "ru": "знать",
        "uk": "знати",
    },
    6064: {
        "en": "a household, especially of servants",
        "es": "casa o familia, especialmente de siervos",
        "ru": "домочадцы, особенно слуги",
        "uk": "домочадці, особливо слуги",
    },
    6065: {
        "en": "a builder or architect",
        "es": "constructor o arquitecto",
        "ru": "строитель или зодчий",
        "uk": "будівничий або архітектор",
    },
    6066: {
        "en": "little faith or lack of trust",
        "es": "poca fe o falta de confianza",
        "ru": "маловерие или недостаток доверия",
        "uk": "маловір'я або нестача довіри",
    },
    6068: {
        "en": "mist or fog",
        "es": "niebla o bruma",
        "ru": "туман или мгла",
        "uk": "туман або імла",
    },
    6069: {
        "en": "everywhere",
        "es": "por todas partes",
        "ru": "повсюду",
        "uk": "повсюди",
    },
    6070: {
        "en": "to insert, interpose, or encamp",
        "es": "insertar, interponer o acampar",
        "ru": "вставлять, помещать между или располагать лагерем",
        "uk": "вставляти, розміщувати між або ставати табором",
    },
    6071: {
        "en": "farther, further, or beyond",
        "es": "más lejos, más adelante o más allá",
        "ru": "дальше, далее или за пределами",
        "uk": "далі, надалі або за межами",
    },
    6072: {
        "en": "to fasten, attach, or kindle",
        "es": "atar, sujetar o encender",
        "ru": "прикреплять, привязывать или зажигать",
        "uk": "прикріплювати, прив'язувати або запалювати",
    },
    6073: {
        "en": "gentleness or meekness",
        "es": "mansedumbre o apacibilidad",
        "ru": "кротость или мягкость нрава",
        "uk": "лагідність або м'якість вдачі",
    },
    6074: {
        "en": "a forefather or ancestor",
        "es": "antepasado o ancestro",
        "ru": "праотец или предок",
        "uk": "праотець або предок",
    },
    6075: {
        "en": "a beggar",
        "es": "mendigo",
        "ru": "нищий",
        "uk": "жебрак",
    },
    6076: {
        "en": "to lean toward or incline",
        "es": "inclinar hacia o hacer inclinar",
        "ru": "наклонять к чему-либо или склонять",
        "uk": "нахиляти до чогось або схиляти",
    },
    6077: {
        "en": "Pyrrhus, a personal name; father of Sopater",
        "es": "Pirro, nombre personal; padre de Sópater",
        "ru": "Пирр, личное имя; отец Сопатра",
        "uk": "Пірр, особове ім'я; батько Сопатра",
    },
    6078: {
        "en": "first or originally",
        "es": "primero u originalmente",
        "ru": "сначала или первоначально",
        "uk": "спершу або первісно",
    },
    6079: {
        "en": "food, provisions, or grain",
        "es": "alimento, provisiones o grano",
        "ru": "пища, припасы или зерно",
        "uk": "їжа, припаси або зерно",
    },
    6080: {
        "en": "a female relative or kinswoman",
        "es": "parienta o mujer de la misma familia",
        "ru": "родственница",
        "uk": "родичка",
    },
    6081: {
        "en": "to fall together, come together, or collapse",
        "es": "caer juntos, encontrarse o derrumbarse",
        "ru": "падать вместе, сходиться или рушиться",
        "uk": "падати разом, сходитися або руйнуватися",
    },
    6083: {
        "en": "to be conscious of or know with oneself",
        "es": "ser consciente o saber dentro de uno mismo",
        "ru": "сознавать или знать внутри себя",
        "uk": "усвідомлювати або знати в собі",
    },
    6085: {
        "en": "a hole, perforation, or opening",
        "es": "agujero, perforación o abertura",
        "ru": "отверстие, прорезь или дыра",
        "uk": "отвір, проріз або діра",
    },
    6087: {
        "en": "superabundantly or far more exceedingly",
        "es": "sobreabundantemente o muchísimo más",
        "ru": "с преизбытком или несравненно больше",
        "uk": "з надлишком або незрівнянно більше",
    },
    6088: {
        "en": "exceedingly or beyond measure",
        "es": "en extremo o más allá de toda medida",
        "ru": "чрезвычайно или сверх меры",
        "uk": "надзвичайно або понад міру",
    },
    6090: {
        "en": "a small ear; the ear",
        "es": "oreja pequeña; oreja",
        "ru": "малое ухо; ухо",
        "uk": "мале вухо; вухо",
    },
    6091: {
        "en": "setting, especially sunset",
        "es": "puesta, especialmente puesta del sol",
        "ru": "заход, особенно заход солнца",
        "uk": "захід, особливо захід сонця",
    },
    6092: {
        "en": "to go out or step out",
        "es": "salir o dar un paso fuera",
        "ru": "выходить или ступать наружу",
        "uk": "виходити або ступати назовні",
    },
    6093: {
        "en": "a pit, especially for storing grain",
        "es": "foso, especialmente para almacenar grano",
        "ru": "яма, особенно для хранения зерна",
        "uk": "яма, особливо для зберігання зерна",
    },
    6094: {
        "en": "to boast",
        "es": "jactarse",
        "ru": "хвалиться",
        "uk": "хвалитися",
    },
    6095: {
        "en": "Arni, a personal name in biblical genealogy",
        "es": "Arní, nombre personal en la genealogía bíblica",
        "ru": "Арни, личное имя в библейской родословной",
        "uk": "Арні, особове ім'я в біблійному родоводі",
    },
    6632: {
        "en": "to withhold, keep back, or deprive",
        "es": "retener, privar o quitar",
        "ru": "удерживать, лишать или отнимать",
        "uk": "утримувати, позбавляти або віднімати",
    },
    6897: {
        "en": "translucent or transparent",
        "es": "traslúcido o transparente",
        "ru": "просвечивающий или прозрачный",
        "uk": "просвічуваний або прозорий",
    },
    7013: {
        "en": "to boast in or pride oneself on",
        "es": "gloriarse en algo o enorgullecerse",
        "ru": "хвалиться чем-либо или гордиться",
        "uk": "хвалитися чимось або пишатися",
    },
    7530: {
        "en": "well done, good, or rightly",
        "es": "bien hecho, bien o correctamente",
        "ru": "хорошо, правильно или молодец",
        "uk": "добре, правильно або молодець",
    },
    9315: {
        "en": "to join in attacking or help put on",
        "es": "unirse al ataque o ayudar a poner",
        "ru": "присоединяться к нападению или помогать надевать",
        "uk": "долучатися до нападу або допомагати накладати",
    },
    9402: {
        "en": "humble-minded or lowly in mind",
        "es": "humilde de mente o de ánimo bajo",
        "ru": "смиренный умом или кроткий духом",
        "uk": "смиренний розумом або лагідний духом",
    },
    9577: {
        "en": "a remnant, remainder, or vestige",
        "es": "resto, remanente o vestigio",
        "ru": "остаток, оставшееся или след",
        "uk": "залишок, решта або слід",
    },
    9990: {
        "en": "twelve as a numeral",
        "es": "doce como numeral",
        "ru": "число двенадцать как числительное",
        "uk": "число дванадцять як числівник",
    },
    9991: {
        "en": "one hundred forty-four as a numeral",
        "es": "ciento cuarenta y cuatro como numeral",
        "ru": "число сто сорок четыре как числительное",
        "uk": "число сто сорок чотири як числівник",
    },
    9992: {
        "en": "figuratively or by way of example",
        "es": "figuradamente o a modo de ejemplo",
        "ru": "образно или в качестве примера",
        "uk": "образно або як приклад",
    },
    9993: {
        "en": "a fold, wrapping, or roll",
        "es": "pliegue, envoltura o rollo",
        "ru": "складка, обертка или сверток",
        "uk": "складка, обгортка або згорток",
    },
    9994: {
        "en": "working at home",
        "es": "que trabaja en casa",
        "ru": "занимающийся домашним трудом",
        "uk": "той, хто працює вдома",
    },
    9995: {
        "en": "sacrificed to idols or offered to a deity",
        "es": "sacrificado a ídolos u ofrecido a una deidad",
        "ru": "принесенный в жертву идолам или божеству",
        "uk": "принесений у жертву ідолам або божеству",
    },
    9996: {
        "en": "to reconcile",
        "es": "reconciliar",
        "ru": "примирять",
        "uk": "примиряти",
    },
    20447: {
        "en": "a stopping, stoppage, or halt",
        "es": "detención, parada o alto",
        "ru": "остановка, прекращение или задержка",
        "uk": "зупинка, припинення або затримка",
    },
    20833: {
        "en": "to desire, long for, or yearn for",
        "es": "desear intensamente o anhelar",
        "ru": "сильно желать, стремиться или тосковать",
        "uk": "сильно бажати, прагнути або тужити",
    },
}

_CYRILLIC_PATTERN = re.compile(r"[А-Яа-яЁёІіЇїЄєҐґ]")
_ENGLISH_START_RE = re.compile(r"^(to|a|an|the)\s+", re.IGNORECASE)


@dataclass(frozen=True)
class ExtendedStrongDescriptionInput:
    id: int
    strong: str
    word: str
    category: str
    source_gloss: str
    tbesg_definition: str
    tflsj_extra_definition: str
    translation_batch_range: tuple[int, int]

    def as_json(self) -> dict[str, object]:
        return {
            "id": self.id,
            "strong": self.strong,
            "word": self.word,
            "category": self.category,
            "source_gloss": self.source_gloss,
            "tbesg_definition": self.tbesg_definition,
            "tflsj_extra_definition": self.tflsj_extra_definition,
            "translation_batch_range": list(self.translation_batch_range),
        }


@dataclass(frozen=True)
class LocalizedDbDescriptionReport:
    locale: str
    db_path: Path
    backup_path: Path | None
    changed_count: int
    existing_extended_count_before: int
    extended_count_after: int
    data_version_before: str
    data_version_after: str

    def as_json(self) -> dict[str, object]:
        return {
            "locale": self.locale,
            "db_path": str(self.db_path),
            "backup_path": str(self.backup_path) if self.backup_path else None,
            "changed_count": self.changed_count,
            "existing_extended_count_before": self.existing_extended_count_before,
            "extended_count_after": self.extended_count_after,
            "data_version_before": self.data_version_before,
            "data_version_after": self.data_version_after,
        }


@dataclass(frozen=True)
class ExtendedStrongDescriptionsApplyReport:
    common_db_path: Path
    applied_at: str
    expected_count: int
    locale_reports: tuple[LocalizedDbDescriptionReport, ...]
    source_inputs_path: Path | None

    def as_json(self) -> dict[str, object]:
        return {
            "common_db_path": str(self.common_db_path),
            "applied_at": self.applied_at,
            "expected_count": self.expected_count,
            "source_inputs_path": str(self.source_inputs_path)
            if self.source_inputs_path
            else None,
            "locale_reports": [report.as_json() for report in self.locale_reports],
        }


@dataclass(frozen=True)
class ExtendedStrongDescriptionsValidationReport:
    common_db_path: Path
    expected_count: int
    locale_counts: dict[str, int]

    def as_json(self) -> dict[str, object]:
        return {
            "common_db_path": str(self.common_db_path),
            "expected_count": self.expected_count,
            "locale_counts": self.locale_counts,
        }


def build_source_description_inputs(
    *,
    common_db_path: Path = DEFAULT_COMMON_DB_PATH,
    bible_module_path: Path = DEFAULT_BIBLE_MODULE_PATH,
    manifest_path: Path = DEFAULT_SOURCE_LOCK_PATH,
    source_paths: Mapping[str, Path] | None = None,
    descriptions: Mapping[int, Mapping[str, str]] = LOCALIZED_EXTENDED_STRONG_DESCRIPTIONS,
    expected_count: int = EXPECTED_ATTESTED_EXTENDED_COUNT,
    expected_primary_count: int = EXPECTED_PRIMARY_ATTESTED_EXTENDED_COUNT,
) -> tuple[ExtendedStrongDescriptionInput, ...]:
    common_ids = _read_common_extended_ids(common_db_path)
    _validate_description_maps(
        descriptions=descriptions,
        expected_ids=common_ids,
        expected_count=expected_count,
    )
    lexicon_index = load_lexicon_index(
        manifest_path=manifest_path,
        source_paths=source_paths,
    )
    rows = build_attested_extended_strong_rows(
        bible_module_path=bible_module_path,
        lexicon_index=lexicon_index,
        expected_attested_count=expected_count,
        expected_primary_count=expected_primary_count,
    )
    row_ids = tuple(row.id for row in rows)
    if row_ids != common_ids:
        raise ValueError(
            "Common DB extended ids do not match attested source rows: "
            f"common={common_ids!r}, source={row_ids!r}"
        )
    _validate_ids_in_content_tool_ranges(common_ids)
    return tuple(
        ExtendedStrongDescriptionInput(
            id=row.id,
            strong=row.strong,
            word=row.word,
            category=row.category,
            source_gloss=row.tbesg_gloss,
            tbesg_definition=row.tbesg_definition,
            tflsj_extra_definition=row.tflsj_extra_definition,
            translation_batch_range=_translation_batch_range_for_id(row.id),
        )
        for row in rows
    )


def apply_extended_strong_descriptions(
    *,
    common_db_path: Path = DEFAULT_COMMON_DB_PATH,
    localized_db_paths: Mapping[str, Path] | None = None,
    descriptions: Mapping[int, Mapping[str, str]] = LOCALIZED_EXTENDED_STRONG_DESCRIPTIONS,
    expected_count: int = EXPECTED_ATTESTED_EXTENDED_COUNT,
    applied_at: str | None = None,
    data_versions: Mapping[str, int] | None = None,
    source_inputs_path: Path | None = None,
) -> ExtendedStrongDescriptionsApplyReport:
    common_db_path = common_db_path.resolve()
    localized_db_paths = _localized_db_paths(localized_db_paths)
    applied_at = applied_at or now_utc_iso()
    common_ids = _read_common_extended_ids(common_db_path)
    _validate_description_maps(
        descriptions=descriptions,
        expected_ids=common_ids,
        expected_count=expected_count,
    )
    _validate_ids_in_content_tool_ranges(common_ids)

    if source_inputs_path is not None:
        _write_json(
            source_inputs_path,
            {
                "generated_at": applied_at,
                "expected_count": expected_count,
                "inputs": [
                    source_input.as_json()
                    for source_input in build_source_description_inputs(
                        common_db_path=common_db_path,
                        descriptions=descriptions,
                        expected_count=expected_count,
                    )
                ],
            },
        )

    backups: dict[str, Path] = {}
    locale_reports: list[LocalizedDbDescriptionReport] = []
    try:
        for locale in SUPPORTED_LOCALES:
            db_path = localized_db_paths[locale].resolve()
            report = _apply_locale_descriptions(
                locale=locale,
                db_path=db_path,
                ids=common_ids,
                descriptions=descriptions,
                applied_at=applied_at,
                data_version=data_versions.get(locale) if data_versions else None,
            )
            locale_reports.append(report)
            if report.backup_path is not None:
                backups[locale] = report.backup_path
    except Exception:
        for locale, backup_path in backups.items():
            shutil.copy2(backup_path, localized_db_paths[locale])
        raise

    validate_localized_extended_descriptions(
        common_db_path=common_db_path,
        localized_db_paths=localized_db_paths,
        descriptions=descriptions,
        expected_count=expected_count,
    )
    return ExtendedStrongDescriptionsApplyReport(
        common_db_path=common_db_path,
        applied_at=applied_at,
        expected_count=expected_count,
        locale_reports=tuple(locale_reports),
        source_inputs_path=source_inputs_path.resolve() if source_inputs_path else None,
    )


def validate_localized_extended_descriptions(
    *,
    common_db_path: Path = DEFAULT_COMMON_DB_PATH,
    localized_db_paths: Mapping[str, Path] | None = None,
    descriptions: Mapping[int, Mapping[str, str]] = LOCALIZED_EXTENDED_STRONG_DESCRIPTIONS,
    expected_count: int = EXPECTED_ATTESTED_EXTENDED_COUNT,
) -> ExtendedStrongDescriptionsValidationReport:
    common_db_path = common_db_path.resolve()
    localized_db_paths = _localized_db_paths(localized_db_paths)
    common_ids = _read_common_extended_ids(common_db_path)
    _validate_description_maps(
        descriptions=descriptions,
        expected_ids=common_ids,
        expected_count=expected_count,
    )
    _validate_ids_in_content_tool_ranges(common_ids)

    locale_counts: dict[str, int] = {}
    for locale in SUPPORTED_LOCALES:
        db_path = localized_db_paths[locale].resolve()
        connection = sqlite3.connect(str(db_path))
        try:
            connection.row_factory = sqlite3.Row
            _validate_localized_dictionary_schema(connection)
            existing = _fetch_existing_descriptions(connection, common_ids)
            missing = [
                strong_id
                for strong_id in common_ids
                if not existing.get(strong_id, "").strip()
            ]
            if missing:
                raise ValueError(
                    f"{db_path.name} is missing localized extended descriptions "
                    f"for: {_preview_ids(missing)}"
                )
            locale_counts[locale] = len(existing)
        finally:
            connection.close()

    return ExtendedStrongDescriptionsValidationReport(
        common_db_path=common_db_path,
        expected_count=expected_count,
        locale_counts=locale_counts,
    )


def _apply_locale_descriptions(
    *,
    locale: str,
    db_path: Path,
    ids: tuple[int, ...],
    descriptions: Mapping[int, Mapping[str, str]],
    applied_at: str,
    data_version: int | None,
) -> LocalizedDbDescriptionReport:
    if not db_path.exists():
        raise FileNotFoundError(f"Localized dictionary DB not found: {db_path}")

    connection = sqlite3.connect(str(db_path))
    try:
        connection.row_factory = sqlite3.Row
        _validate_localized_dictionary_schema(connection)
        existing = _fetch_existing_descriptions(connection, ids)
        existing_extended_count_before = len(
            [strong_id for strong_id in ids if existing.get(strong_id, "").strip()]
        )
        rows_to_write = [
            (strong_id, descriptions[strong_id][locale].strip())
            for strong_id in ids
            if existing.get(strong_id, "") != descriptions[strong_id][locale].strip()
        ]
        metadata_before = _read_db_metadata(connection)
        data_version_before = metadata_before.get(DB_METADATA_DATA_VERSION_KEY, "0")
        data_version_after = str(
            data_version if data_version is not None else int(data_version_before) + 1
        )
        backup_path: Path | None = None
        if rows_to_write:
            backup_path = _backup_db(db_path, applied_at)
            with connection:
                connection.executemany(
                    """
                    INSERT INTO greek_descs(id, desc)
                    VALUES(?, ?)
                    ON CONFLICT(id) DO UPDATE SET desc = excluded.desc
                    """,
                    rows_to_write,
                )
                _set_db_metadata(
                    connection,
                    data_version=data_version_after,
                    date_iso=applied_at,
                )
        else:
            data_version_after = data_version_before

        after = _fetch_existing_descriptions(connection, ids)
        return LocalizedDbDescriptionReport(
            locale=locale,
            db_path=db_path,
            backup_path=backup_path,
            changed_count=len(rows_to_write),
            existing_extended_count_before=existing_extended_count_before,
            extended_count_after=len(
                [strong_id for strong_id in ids if after.get(strong_id, "").strip()]
            ),
            data_version_before=data_version_before,
            data_version_after=data_version_after,
        )
    finally:
        connection.close()


def _localized_db_paths(paths: Mapping[str, Path] | None) -> dict[str, Path]:
    if paths is None:
        paths = {
            locale: DEFAULT_DB_DIR / f"revelation_{locale}.sqlite"
            for locale in SUPPORTED_LOCALES
        }
    missing = [locale for locale in SUPPORTED_LOCALES if locale not in paths]
    if missing:
        raise ValueError(f"Missing localized DB paths: {', '.join(missing)}")
    return {locale: Path(paths[locale]) for locale in SUPPORTED_LOCALES}


def _read_common_extended_ids(common_db_path: Path) -> tuple[int, ...]:
    if not common_db_path.exists():
        raise FileNotFoundError(f"Common dictionary DB not found: {common_db_path}")
    connection = sqlite3.connect(str(common_db_path))
    try:
        rows = connection.execute(
            """
            SELECT id
            FROM greek_words
            WHERE id > ?
            ORDER BY id
            """,
            (CLASSIC_GREEK_STRONG_MAX,),
        ).fetchall()
    finally:
        connection.close()

    ids = tuple(int(row[0]) for row in rows)
    if UNUSED_EXTENDED_SENTINEL in {f"G{strong_id}" for strong_id in ids}:
        raise ValueError(f"Unused extended sentinel {UNUSED_EXTENDED_SENTINEL} is present")
    return ids


def _validate_description_maps(
    *,
    descriptions: Mapping[int, Mapping[str, str]],
    expected_ids: tuple[int, ...],
    expected_count: int,
) -> None:
    if len(expected_ids) != expected_count:
        raise ValueError(
            f"Expected {expected_count} common extended ids, found {len(expected_ids)}"
        )
    description_ids = tuple(sorted(int(strong_id) for strong_id in descriptions))
    if description_ids != expected_ids:
        raise ValueError(
            "Localized description ids do not match common extended ids: "
            f"descriptions={description_ids!r}, common={expected_ids!r}"
        )
    for strong_id in expected_ids:
        localized = descriptions[strong_id]
        missing_locales = [
            locale
            for locale in SUPPORTED_LOCALES
            if not localized.get(locale, "").strip()
        ]
        if missing_locales:
            raise ValueError(
                f"G{strong_id} is missing translations for: {', '.join(missing_locales)}"
            )
        _validate_translation_quality(strong_id, localized)


def _validate_translation_quality(strong_id: int, localized: Mapping[str, str]) -> None:
    english = localized["en"].strip()
    if _CYRILLIC_PATTERN.search(english):
        raise ValueError(f"G{strong_id} English description contains Cyrillic text")

    spanish = localized["es"].strip()
    if _CYRILLIC_PATTERN.search(spanish):
        raise ValueError(f"G{strong_id} Spanish description contains Cyrillic text")
    if _ENGLISH_START_RE.search(spanish):
        raise ValueError(f"G{strong_id} Spanish description appears untranslated")
    if spanish == english:
        raise ValueError(f"G{strong_id} Spanish description matches English")

    for locale in ("ru", "uk"):
        text = localized[locale].strip()
        if not _CYRILLIC_PATTERN.search(text):
            raise ValueError(f"G{strong_id} {locale} description appears untranslated")
        if text == english:
            raise ValueError(f"G{strong_id} {locale} description matches English")


def _validate_ids_in_content_tool_ranges(ids: Sequence[int]) -> None:
    extended_ranges = _extended_translation_batch_ranges()
    missing = [
        strong_id
        for strong_id in ids
        if not any(start <= strong_id <= end for start, end in extended_ranges)
    ]
    if missing:
        raise ValueError(
            "Extended ids are missing from content-tool translation ranges: "
            f"{_preview_ids(missing)}"
        )


def _extended_translation_batch_ranges() -> tuple[tuple[int, int], ...]:
    return tuple(
        (start, end)
        for start, end in GREEK_DESC_GROUP_RANGES
        if start > CLASSIC_GREEK_STRONG_MAX
    )


def _translation_batch_range_for_id(strong_id: int) -> tuple[int, int]:
    for start, end in _extended_translation_batch_ranges():
        if start <= strong_id <= end:
            return (start, end)
    raise ValueError(f"G{strong_id} is outside content-tool translation ranges")


def _validate_localized_dictionary_schema(connection: sqlite3.Connection) -> None:
    greek_desc_columns = {
        row["name"]
        for row in connection.execute("PRAGMA table_info(greek_descs)").fetchall()
    }
    if {"id", "desc"} - greek_desc_columns:
        raise ValueError("Localized DB greek_descs table is missing id/desc columns")

    metadata_columns = {
        row["name"]
        for row in connection.execute("PRAGMA table_info(db_metadata)").fetchall()
    }
    if {"key", "value"} - metadata_columns:
        raise ValueError("Localized DB db_metadata table is missing key/value columns")


def _fetch_existing_descriptions(
    connection: sqlite3.Connection,
    ids: Sequence[int],
) -> dict[int, str]:
    placeholders = ",".join("?" for _ in ids)
    rows = connection.execute(
        f"SELECT id, desc FROM greek_descs WHERE id IN ({placeholders})",
        tuple(ids),
    ).fetchall()
    return {int(row["id"]): str(row["desc"]) for row in rows}


def _read_db_metadata(connection: sqlite3.Connection) -> dict[str, str]:
    return {
        str(row["key"]): str(row["value"])
        for row in connection.execute("SELECT key, value FROM db_metadata")
    }


def _set_db_metadata(
    connection: sqlite3.Connection,
    *,
    data_version: str,
    date_iso: str,
) -> None:
    connection.executemany(
        """
        INSERT INTO db_metadata(key, value)
        VALUES(?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """,
        (
            (DB_METADATA_DATA_VERSION_KEY, data_version),
            (DB_METADATA_DATE_KEY, date_iso),
        ),
    )


def _backup_db(db_path: Path, timestamp: str) -> Path:
    backup_path = db_path.with_name(f"{db_path.name}.{_filesystem_timestamp(timestamp)}.bak")
    shutil.copy2(db_path, backup_path)
    return backup_path


def _filesystem_timestamp(value: str) -> str:
    return "".join(character if character.isalnum() else "-" for character in value)


def _write_json(path: Path, data: Mapping[str, object]) -> None:
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _preview_ids(ids: Sequence[int]) -> str:
    values = list(ids)
    preview = ", ".join(f"G{strong_id}" for strong_id in values[:10])
    return preview if len(values) <= 10 else f"{preview}, ..."


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fill localized greek_descs rows for NA28_LXX-attested extended Strong entries.",
    )
    parser.add_argument(
        "--common-db",
        type=Path,
        default=DEFAULT_COMMON_DB_PATH,
        help="Path to common revelation.sqlite.",
    )
    parser.add_argument(
        "--write-inputs",
        type=Path,
        default=None,
        help="Optional JSON path for generated source description inputs.",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate localized DB coverage without writing rows.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.validate_only:
        report = validate_localized_extended_descriptions(common_db_path=args.common_db)
        print(json.dumps(report.as_json(), ensure_ascii=False, indent=2))
        return 0

    report = apply_extended_strong_descriptions(
        common_db_path=args.common_db,
        source_inputs_path=args.write_inputs,
    )
    print(json.dumps(report.as_json(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
