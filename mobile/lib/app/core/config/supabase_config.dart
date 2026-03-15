class SupabaseConfig {
  const SupabaseConfig({
    required this.url,
    required this.anonKey,
  });

  final String url;
  final String anonKey;

  bool get isConfigured => url.isNotEmpty && anonKey.isNotEmpty;

  static const SupabaseConfig fromEnvironment = SupabaseConfig(
    url: String.fromEnvironment("SUPABASE_URL", defaultValue: ""),
    anonKey: String.fromEnvironment("SUPABASE_ANON_KEY", defaultValue: ""),
  );
}
