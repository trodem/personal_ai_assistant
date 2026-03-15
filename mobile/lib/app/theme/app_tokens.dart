import 'package:flutter/material.dart';

class AppColors {
  static const Color canvas = Color(0xFFF7F4EE);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color ink = Color(0xFF1F2A37);
  static const Color mutedInk = Color(0xFF5A6573);
  static const Color accent = Color(0xFF1F6F5E);
  static const Color accentStrong = Color(0xFF15574A);
  static const Color onAccent = Color(0xFFFFFFFF);
  static const Color border = Color(0xFFD8E0E8);
  static const Color danger = Color(0xFFB42318);
}

class AppSpacing {
  static const double xs = 8;
  static const double sm = 12;
  static const double md = 16;
  static const double lg = 24;
  static const double xl = 32;
}

class AppRadii {
  static const double md = 14;
  static const double lg = 20;
}

class AppShadows {
  static const List<BoxShadow> card = <BoxShadow>[
    BoxShadow(
      color: Color(0x16000000),
      offset: Offset(0, 6),
      blurRadius: 24,
      spreadRadius: -6,
    ),
  ];
}

class AppTextStyles {
  static const TextStyle buttonPrimary = TextStyle(
    fontSize: 15,
    fontWeight: FontWeight.w700,
  );

  static const TextStyle buttonSecondary = TextStyle(
    fontSize: 14,
    fontWeight: FontWeight.w700,
  );

  static const TextStyle sectionTitle = TextStyle(
    fontSize: 18,
    fontWeight: FontWeight.w700,
  );

  static const TextStyle error = TextStyle(
    color: AppColors.danger,
    fontSize: 14,
    fontWeight: FontWeight.w500,
  );
}
