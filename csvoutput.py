
import io
import csv

def createMessage(strage, nation, vehicle, chassis, turret, gun, shell):
    output = io.StringIO(newline='')
    writer = csv.writer(output, dialect='excel', lineterminator='\n')
        
    vehicleInfo = strage.fetchVehicleInfo(nation, vehicle)
    chassisInfo = strage.fetchChassisInfo(nation, vehicle, chassis)
    turretInfo = strage.fetchTurretInfo(nation, vehicle, turret)
    gunInfo = strage.fetchGunInfo(nation, vehicle, turret, gun)
    shellInfo = strage.fetchShellInfo(nation, gun, shell)
    
    writer.writerow([ 'vehicle', vehicleInfo['name'], vehicleInfo['id'], vehicleInfo['shortUserString'], vehicleInfo['description'] ])
    writer.writerow([ 'chassis', chassisInfo['name'], chassisInfo['tag'] ])
    writer.writerow([ 'turret', turretInfo['name'], turretInfo['tag'] ])
    writer.writerow([ 'gun', gunInfo['name'], gunInfo['tag'] ])
    writer.writerow([ 'shell', shellInfo['name'], shellInfo['tag'] ])

    writer.writerow([ 'reloadTime', gunInfo['reloadTime'], 's' ])
    writer.writerow([ 'aimingTime', gunInfo['aimingTime'], 's' ])
    writer.writerow([ 'shotDispersionRadius', gunInfo['shotDispersionRadius'], 'm' ])
    writer.writerow([ 'vehicleMovement', chassisInfo['vehicleMovement'], '' ])
    writer.writerow([ 'vehicleRotation', chassisInfo['vehicleRotation'], '' ])
    writer.writerow([ 'turretRotation', gunInfo['turretRotation'], '' ])
    writer.writerow([ 'afterShot', gunInfo['afterShot'], '' ])
    writer.writerow([ 'whileGunDamaged', gunInfo['whileGunDamaged'], '' ])

    return output.getvalue()
