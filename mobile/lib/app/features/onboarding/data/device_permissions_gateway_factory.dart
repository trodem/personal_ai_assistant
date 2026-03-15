import '../domain/device_permissions_gateway.dart';
import 'permission_handler_gateway.dart';

class DevicePermissionsGatewayFactory {
  static DevicePermissionsGateway create() {
    return PermissionHandlerGateway();
  }
}
