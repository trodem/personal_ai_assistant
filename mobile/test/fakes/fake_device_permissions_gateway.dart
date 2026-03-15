import 'package:personal_ai_assistant_mobile/app/features/onboarding/domain/device_permissions_gateway.dart';

class FakeDevicePermissionsGateway implements DevicePermissionsGateway {
  FakeDevicePermissionsGateway({
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
}
