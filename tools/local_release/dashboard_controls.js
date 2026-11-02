(function(root){
'use strict';
function supportsLinux(project){return (project.hosts||[]).includes('linux');}
function policy(project){
 if(project.automatic_builds)return 'Автобилд подключён. Панель: 10 с в покое, 3 с при сборке.';
 return 'Автобилд ожидает полного пробного выпуска. Доступно ручное управление.'+(supportsLinux(project)?' Приём Linux-пакетов подключён.':'');
}
function actions(release,host){
 if(!release.controllable||release.publication?.published)return [];
 if(release.active)return [['restart','Перезапустить'],['stop','Остановить']];
 const local=release.hosts?.[host];
 const attempted=local?.steps?.length>0||['failed','stopped','interrupted','built','incomplete'].includes(local?.status)||release.stop_requested;
 const result=[[attempted?'retry':'start',attempted?'Повторить':'Запустить']];
 if(!release.stop_requested&&local?.status!=='stopped'&&local?.missing?.length!==0)result.push(['stop','Остановить']);
 return result;
}
function description(action,release,host){
 const local=release.hosts?.[host],where=host==='windows'?'Windows':host==='linux'?'Linux':host;
 const waiting=release.waiting_hosts?.length?' Остальные ОС ('+release.waiting_hosts.join(', ')+') выполняют свои этапы отдельно.':'';
 const cached=' Уже проверенные этапы и пакеты сохраняются; изменённые или отсутствующие результаты будут созданы заново.';
 if(action==='delete')return 'Откроет диалог подтверждения удаления '+release.version+' +'+release.build+'. После подтверждения удалит пакеты, журналы и рабочую копию этой сборки на компьютере и соответствующий GitHub Release. Исходный Git-код и тег сохраняются.';
 if(action==='cancel-delete')return 'Закроет диалог. Запрос удаления не будет отправлен.';
 if(action==='confirm-delete')return 'Подтвердит необратимое удаление локальных пакетов, журналов и временных файлов выбранной сборки и соответствующего GitHub Release. Активная сборка сначала будет остановлена.';
 if(action==='retry-delete')return 'Повторит незавершённую очистку по уже подтверждённому запросу. Уже удалённый GitHub Release повторно не удаляется; данные остальных сборок сохраняются.';
 if(action==='stop')return 'Запросит остановку этого задания на '+where+'. Текущая команда будет остановлена, затем восстановятся данные приёмки и журнал будет отправлен на GitHub. При недоступной сети отправка останется в очереди.'+waiting;
 const remoteResume=host==='windows'&&local?.missing?.length===0&&release.waiting_hosts?.includes('linux')?' Также отправит Linux запрос продолжения при следующем входе.':'';
 if(action==='restart')return (release.active?'Сначала остановит активный процесс и дождётся сохранения результата. Затем ':'Снимет прежний запрос остановки и ')+ 'возобновит задание на '+where+'. Это продолжение по контрольным точкам.'+cached+remoteResume+waiting;
 if(release.active)return 'Сейчас это задание уже выполняется на '+where+'. Для нового запуска сначала дождитесь завершения или запросите остановку.';
 if(local?.missing?.length===0)return 'Все обязательные этапы '+where+' уже пройдены. Проверит их сохранённые результаты и повторит необходимый обмен/публикацию. Полный релиз появится после готовности остальных ОС.'+remoteResume+waiting;
 return (action==='retry'?'Повторит неудачные и незавершённые этапы':'Запустит или продолжит этапы этого задания')+' на '+where+'. Снимет прежний запрос остановки.'+cached+waiting;
}
function attach(button,message){
 button.dataset.help=message;button.setAttribute('aria-description',message);
 const doc=button.ownerDocument,wrapper=doc.createElement('span');wrapper.className='tooltip-trigger';
 if(button.disabled){wrapper.tabIndex=0;wrapper.setAttribute('aria-label',button.textContent);wrapper.setAttribute('aria-description',message);}
 wrapper.append(button);
 function hide(){const tip=doc.getElementById('controlTooltip');if(tip)tip.hidden=true;}
 function show(){
  let tip=doc.getElementById('controlTooltip');if(!tip){tip=doc.createElement('div');tip.id='controlTooltip';tip.className='control-tooltip';tip.setAttribute('role','tooltip');doc.body.append(tip);}
  const layer=button.closest('dialog[open]')||doc.body;if(tip.parentNode!==layer)layer.append(tip);
  tip.textContent=button.dataset.help;tip.hidden=false;button.setAttribute('aria-describedby',tip.id);
  const view=doc.defaultView,r=wrapper.getBoundingClientRect();tip.style.maxWidth=Math.max(150,Math.min(370,view.innerWidth-24))+'px';
  const box=tip.getBoundingClientRect();tip.style.left=Math.max(12,Math.min(r.left,view.innerWidth-box.width-12))+'px';
  tip.style.top=Math.max(12,r.bottom+8+box.height>view.innerHeight?r.top-box.height-8:r.bottom+8)+'px';
 }
 wrapper.addEventListener('mouseenter',show);wrapper.addEventListener('mouseleave',hide);wrapper.addEventListener('focusin',show);wrapper.addEventListener('focusout',hide);
 wrapper.addEventListener('click',hide);wrapper.addEventListener('keydown',e=>{if(e.key==='Escape')hide();});
 return wrapper;
}
const api={actions,description,attach,supportsLinux,policy};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.buildControls=api;
})(typeof window!=='undefined'?window:this);
