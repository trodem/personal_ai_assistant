enum AppPermission {
  microphone,
  camera,
}

abstract class DevicePermissionsGateway {
  Future<bool> request(AppPermission permission);
}
