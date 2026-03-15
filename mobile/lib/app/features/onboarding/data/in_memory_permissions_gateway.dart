import '../domain/device_permissions_gateway.dart';

class InMemoryPermissionsGateway implements DevicePermissionsGateway {
  InMemoryPermissionsGateway({
    this.microphoneGranted = true,
    this.cameraGranted = true,
  });

  bool microphoneGranted;
  bool cameraGranted;

  @override
  Future<bool> request(AppPermission permission) async {
    switch (permission) {
      case AppPermission.microphone:
        return microphoneGranted;
      case AppPermission.camera:
        return cameraGranted;
    }
  }

  @override
  Future<bool> openSettings() async {
    return false;
  }
}
