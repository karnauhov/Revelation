import "package:flutter/material.dart";

class MaterialTheme {
  static ColorScheme getColorTheme(String key) {
    switch (key) {
      case 'manuscript':
        return manuscript();
      case 'forest':
        return forest();
      case 'sky':
        return sky();
      case 'grape':
        return grape();
      default:
        return manuscript();
    }
  }

  static TextTheme getTextTheme(BuildContext context, String key) {
    switch (key) {
      case 'small':
        return getScaledTextTheme(context, 1);
      case 'medium':
        return getScaledTextTheme(context, 1.15);
      case 'large':
        return getScaledTextTheme(context, 1.3);
      default:
        return getScaledTextTheme(context, 1.15);
    }
  }

  static ColorScheme manuscript() {
    return const ColorScheme(
      brightness: Brightness.light,
      primary: Color(0xff6d5e0f),
      surfaceTint: Color(0xff6d5e0f),
      onPrimary: Color(0xffffffff),
      primaryContainer: Color(0xfff8e287),
      onPrimaryContainer: Color(0xff534600),
      secondary: Color(0xff665e40),
      onSecondary: Color(0xffffffff),
      secondaryContainer: Color(0xffeee2bc),
      onSecondaryContainer: Color(0xff4e472a),
      tertiary: Color(0xff43664e),
      onTertiary: Color(0xffffffff),
      tertiaryContainer: Color(0xffc5ecce),
      onTertiaryContainer: Color(0xff2c4e38),
      error: Color(0xffba1a1a),
      onError: Color(0xffffffff),
      errorContainer: Color(0xffffdad6),
      onErrorContainer: Color(0xff93000a),
      surface: Color(0xfffff9ee),
      onSurface: Color(0xff1e1b13),
      onSurfaceVariant: Color(0xff4b4739),
      outline: Color(0xff7c7767),
      outlineVariant: Color(0xffcdc6b4),
      shadow: Color(0xff000000),
      scrim: Color(0xff000000),
      inverseSurface: Color(0xff333027),
      inversePrimary: Color(0xffdbc66e),
      primaryFixed: Color(0xfff8e287),
      onPrimaryFixed: Color(0xff221b00),
      primaryFixedDim: Color(0xffdbc66e),
      onPrimaryFixedVariant: Color(0xff534600),
      secondaryFixed: Color(0xffeee2bc),
      onSecondaryFixed: Color(0xff211b04),
      secondaryFixedDim: Color(0xffd1c6a1),
      onSecondaryFixedVariant: Color(0xff4e472a),
      tertiaryFixed: Color(0xffc5ecce),
      onTertiaryFixed: Color(0xff00210f),
      tertiaryFixedDim: Color(0xffa9d0b3),
      onTertiaryFixedVariant: Color(0xff2c4e38),
      surfaceDim: Color(0xffe0d9cc),
      surfaceBright: Color(0xfffff9ee),
      surfaceContainerLowest: Color(0xffffffff),
      surfaceContainerLow: Color(0xfffaf3e5),
      surfaceContainer: Color(0xfff4eddf),
      surfaceContainerHigh: Color(0xffeee8da),
      surfaceContainerHighest: Color(0xffe8e2d4),
    );
  }

  static ColorScheme forest() {
    return const ColorScheme(
      brightness: Brightness.light,
      primary: Color(0xff3e6700),
      surfaceTint: Color(0xff3f6900),
      onPrimary: Color(0xffffffff),
      primaryContainer: Color(0xff4f8200),
      onPrimaryContainer: Color(0xfff9ffea),
      secondary: Color(0xff4b662a),
      onSecondary: Color(0xffffffff),
      secondaryContainer: Color(0xffcceea1),
      onSecondaryContainer: Color(0xff516d2f),
      tertiary: Color(0xff00694e),
      onTertiary: Color(0xffffffff),
      tertiaryContainer: Color(0xff008564),
      onTertiaryContainer: Color(0xfff5fff8),
      error: Color(0xffba1a1a),
      onError: Color(0xffffffff),
      errorContainer: Color(0xffffdad6),
      onErrorContainer: Color(0xff93000a),
      surface: Color(0xfff7fbea),
      onSurface: Color(0xff191d13),
      onSurfaceVariant: Color(0xff424937),
      outline: Color(0xff727a66),
      outlineVariant: Color(0xffc2cab2),
      shadow: Color(0xff000000),
      scrim: Color(0xff000000),
      inverseSurface: Color(0xff2e3227),
      inversePrimary: Color(0xff97d945),
      primaryFixed: Color(0xffb2f65f),
      onPrimaryFixed: Color(0xff102000),
      primaryFixedDim: Color(0xff97d945),
      onPrimaryFixedVariant: Color(0xff2f4f00),
      secondaryFixed: Color(0xffcceea1),
      onSecondaryFixed: Color(0xff102000),
      secondaryFixedDim: Color(0xffb1d188),
      onSecondaryFixedVariant: Color(0xff344e14),
      tertiaryFixed: Color(0xff7cf9cb),
      onTertiaryFixed: Color(0xff002116),
      tertiaryFixedDim: Color(0xff5ddcb0),
      onTertiaryFixedVariant: Color(0xff00513c),
      surfaceDim: Color(0xffd8dccc),
      surfaceBright: Color(0xfff7fbea),
      surfaceContainerLowest: Color(0xffffffff),
      surfaceContainerLow: Color(0xfff2f5e5),
      surfaceContainer: Color(0xffecf0df),
      surfaceContainerHigh: Color(0xffe6eada),
      surfaceContainerHighest: Color(0xffe0e4d4),
    );
  }

  static ColorScheme sky() {
    return const ColorScheme(
      brightness: Brightness.light,
      primary: Color(0xff0c6780),
      surfaceTint: Color(0xff0c6780),
      onPrimary: Color(0xffffffff),
      primaryContainer: Color(0xff87ceeb),
      onPrimaryContainer: Color(0xff005870),
      secondary: Color(0xff49626d),
      onSecondary: Color(0xffffffff),
      secondaryContainer: Color(0xffcce7f4),
      onSecondaryContainer: Color(0xff4f6873),
      tertiary: Color(0xff745086),
      onTertiary: Color(0xffffffff),
      tertiaryContainer: Color(0xffe0b5f2),
      onTertiaryContainer: Color(0xff664378),
      error: Color(0xffba1a1a),
      onError: Color(0xffffffff),
      errorContainer: Color(0xffffdad6),
      onErrorContainer: Color(0xff93000a),
      surface: Color(0xfff7f9fc),
      onSurface: Color(0xff191c1e),
      onSurfaceVariant: Color(0xff3f484c),
      outline: Color(0xff6f787d),
      outlineVariant: Color(0xffbfc8cd),
      shadow: Color(0xff000000),
      scrim: Color(0xff000000),
      inverseSurface: Color(0xff2d3133),
      inversePrimary: Color(0xff89d0ed),
      primaryFixed: Color(0xffbaeaff),
      onPrimaryFixed: Color(0xff001f29),
      primaryFixedDim: Color(0xff89d0ed),
      onPrimaryFixedVariant: Color(0xff004d62),
      secondaryFixed: Color(0xffcce7f4),
      onSecondaryFixed: Color(0xff031f28),
      secondaryFixedDim: Color(0xffb0cbd7),
      onSecondaryFixedVariant: Color(0xff314a55),
      tertiaryFixed: Color(0xfff6d9ff),
      onTertiaryFixed: Color(0xff2c0b3e),
      tertiaryFixedDim: Color(0xffe2b7f4),
      onTertiaryFixedVariant: Color(0xff5b396d),
      surfaceDim: Color(0xffd8dadc),
      surfaceBright: Color(0xfff7f9fc),
      surfaceContainerLowest: Color(0xffffffff),
      surfaceContainerLow: Color(0xfff2f4f6),
      surfaceContainer: Color(0xffeceef0),
      surfaceContainerHigh: Color(0xffe6e8ea),
      surfaceContainerHighest: Color(0xffe0e3e5),
    );
  }

  static ColorScheme grape() {
    return const ColorScheme(
      brightness: Brightness.light,
      primary: Color(0xff56088f),
      surfaceTint: Color(0xff7e3db7),
      onPrimary: Color(0xffffffff),
      primaryContainer: Color(0xff6f2da8),
      onPrimaryContainer: Color(0xffdcb3ff),
      secondary: Color(0xff6d5484),
      onSecondary: Color(0xffffffff),
      secondaryContainer: Color(0xffe5c6fd),
      onSecondaryContainer: Color(0xff694f7f),
      tertiary: Color(0xff73004d),
      onTertiary: Color(0xffffffff),
      tertiaryContainer: Color(0xff922066),
      onTertiaryContainer: Color(0xffffaad2),
      error: Color(0xffba1a1a),
      onError: Color(0xffffffff),
      errorContainer: Color(0xffffdad6),
      onErrorContainer: Color(0xff93000a),
      surface: Color(0xfffff7fe),
      onSurface: Color(0xff1e1a22),
      onSurfaceVariant: Color(0xff4c4452),
      outline: Color(0xff7e7483),
      outlineVariant: Color(0xffcfc2d4),
      shadow: Color(0xff000000),
      scrim: Color(0xff000000),
      inverseSurface: Color(0xff342f37),
      inversePrimary: Color(0xffdeb7ff),
      primaryFixed: Color(0xfff1dbff),
      onPrimaryFixed: Color(0xff2d0050),
      primaryFixedDim: Color(0xffdeb7ff),
      onPrimaryFixedVariant: Color(0xff65209d),
      secondaryFixed: Color(0xfff1dbff),
      onSecondaryFixed: Color(0xff27103c),
      secondaryFixedDim: Color(0xffdabbf2),
      onSecondaryFixedVariant: Color(0xff553c6a),
      tertiaryFixed: Color(0xffffd8e8),
      onTertiaryFixed: Color(0xff3d0027),
      tertiaryFixedDim: Color(0xffffafd5),
      onTertiaryFixedVariant: Color(0xff85135c),
      surfaceDim: Color(0xffe1d7e2),
      surfaceBright: Color(0xfffff7fe),
      surfaceContainerLowest: Color(0xffffffff),
      surfaceContainerLow: Color(0xfffbf0fc),
      surfaceContainer: Color(0xfff5ebf6),
      surfaceContainerHigh: Color(0xffefe5f0),
      surfaceContainerHighest: Color(0xffe9dfea),
    );
  }

  static TextTheme getScaledTextTheme(BuildContext context, double scale) {
    final TextTheme textTheme = Theme.of(context).textTheme;
    return TextTheme(
      displayLarge: textTheme.displayLarge?.copyWith(
        fontSize: textTheme.displayLarge?.fontSize != null
            ? textTheme.displayLarge!.fontSize! * scale
            : null,
        letterSpacing: textTheme.displayLarge?.letterSpacing != null
            ? textTheme.displayLarge!.letterSpacing! * scale
            : null,
      ),
      displayMedium: textTheme.displayMedium?.copyWith(
        fontSize: textTheme.displayMedium?.fontSize != null
            ? textTheme.displayMedium!.fontSize! * scale
            : null,
        letterSpacing: textTheme.displayMedium?.letterSpacing != null
            ? textTheme.displayMedium!.letterSpacing! * scale
            : null,
      ),
      displaySmall: textTheme.displaySmall?.copyWith(
        fontSize: textTheme.displaySmall?.fontSize != null
            ? textTheme.displaySmall!.fontSize! * scale
            : null,
        letterSpacing: textTheme.displaySmall?.letterSpacing != null
            ? textTheme.displaySmall!.letterSpacing! * scale
            : null,
      ),
      headlineLarge: textTheme.headlineLarge?.copyWith(
        fontSize: textTheme.headlineLarge?.fontSize != null
            ? textTheme.headlineLarge!.fontSize! * scale
            : null,
        letterSpacing: textTheme.headlineLarge?.letterSpacing != null
            ? textTheme.headlineLarge!.letterSpacing! * scale
            : null,
      ),
      headlineMedium: textTheme.headlineMedium?.copyWith(
        fontSize: textTheme.headlineMedium?.fontSize != null
            ? textTheme.headlineMedium!.fontSize! * scale
            : null,
        letterSpacing: textTheme.headlineMedium?.letterSpacing != null
            ? textTheme.headlineMedium!.letterSpacing! * scale
            : null,
      ),
      headlineSmall: textTheme.headlineSmall?.copyWith(
        fontSize: textTheme.headlineSmall?.fontSize != null
            ? textTheme.headlineSmall!.fontSize! * scale
            : null,
        letterSpacing: textTheme.headlineSmall?.letterSpacing != null
            ? textTheme.headlineSmall!.letterSpacing! * scale
            : null,
      ),
      titleLarge: textTheme.titleLarge?.copyWith(
        fontSize: textTheme.titleLarge?.fontSize != null
            ? textTheme.titleLarge!.fontSize! * scale
            : null,
        letterSpacing: textTheme.titleLarge?.letterSpacing != null
            ? textTheme.titleLarge!.letterSpacing! * scale
            : null,
      ),
      titleMedium: textTheme.titleMedium?.copyWith(
        fontSize: textTheme.titleMedium?.fontSize != null
            ? textTheme.titleMedium!.fontSize! * scale
            : null,
        letterSpacing: textTheme.titleMedium?.letterSpacing != null
            ? textTheme.titleMedium!.letterSpacing! * scale
            : null,
      ),
      titleSmall: textTheme.titleSmall?.copyWith(
        fontSize: textTheme.titleSmall?.fontSize != null
            ? textTheme.titleSmall!.fontSize! * scale
            : null,
        letterSpacing: textTheme.titleSmall?.letterSpacing != null
            ? textTheme.titleSmall!.letterSpacing! * scale
            : null,
      ),
      bodyLarge: textTheme.bodyLarge?.copyWith(
        fontSize: textTheme.bodyLarge?.fontSize != null
            ? textTheme.bodyLarge!.fontSize! * scale
            : null,
        letterSpacing: textTheme.bodyLarge?.letterSpacing != null
            ? textTheme.bodyLarge!.letterSpacing! * scale
            : null,
      ),
      bodyMedium: textTheme.bodyMedium?.copyWith(
        fontSize: textTheme.bodyMedium?.fontSize != null
            ? textTheme.bodyMedium!.fontSize! * scale
            : null,
        letterSpacing: textTheme.bodyMedium?.letterSpacing != null
            ? textTheme.bodyMedium!.letterSpacing! * scale
            : null,
      ),
      bodySmall: textTheme.bodySmall?.copyWith(
        fontSize: textTheme.bodySmall?.fontSize != null
            ? textTheme.bodySmall!.fontSize! * scale
            : null,
        letterSpacing: textTheme.bodySmall?.letterSpacing != null
            ? textTheme.bodySmall!.letterSpacing! * scale
            : null,
      ),
      labelLarge: textTheme.labelLarge?.copyWith(
        fontSize: textTheme.labelLarge?.fontSize != null
            ? textTheme.labelLarge!.fontSize! * scale
            : null,
        letterSpacing: textTheme.labelLarge?.letterSpacing != null
            ? textTheme.labelLarge!.letterSpacing! * scale
            : null,
      ),
      labelMedium: textTheme.labelMedium?.copyWith(
        fontSize: textTheme.labelMedium?.fontSize != null
            ? textTheme.labelMedium!.fontSize! * scale
            : null,
        letterSpacing: textTheme.labelMedium?.letterSpacing != null
            ? textTheme.labelMedium!.letterSpacing! * scale
            : null,
      ),
      labelSmall: textTheme.labelSmall?.copyWith(
        fontSize: textTheme.labelSmall?.fontSize != null
            ? textTheme.labelSmall!.fontSize! * scale
            : null,
        letterSpacing: textTheme.labelSmall?.letterSpacing != null
            ? textTheme.labelSmall!.letterSpacing! * scale
            : null,
      ),
    );
  }
}
