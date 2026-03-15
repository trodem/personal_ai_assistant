class ApiConfig {
  const ApiConfig({
    required this.baseUrl,
  });

  final String baseUrl;

  bool get isConfigured => baseUrl.isNotEmpty;

  static const ApiConfig fromEnvironment = ApiConfig(
    baseUrl: String.fromEnvironment("API_BASE_URL", defaultValue: ""),
  );
}
