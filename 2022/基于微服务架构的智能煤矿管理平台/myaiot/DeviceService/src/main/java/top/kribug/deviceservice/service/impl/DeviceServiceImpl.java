package top.kribug.deviceservice.service.impl;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;
import top.kribug.deviceservice.entity.Device;
import top.kribug.deviceservice.entity.Model;
import top.kribug.deviceservice.entity.Room;
import top.kribug.deviceservice.entity.User;
import top.kribug.deviceservice.feign.FeignRoomClient;
import top.kribug.deviceservice.mapper.DeviceMapper;
import top.kribug.deviceservice.service.DeviceService;
import top.kribug.deviceservice.service.ModelService;

import java.util.Date;
import java.util.HashMap;
import java.util.List;

@Service
public class DeviceServiceImpl implements DeviceService {

    @Autowired
    private DeviceMapper deviceMapper;
    @Autowired
    private RedisTemplate<String, String> redisTemplate;
    @Override
    public List<Device> selectAllDevice() {
        return deviceMapper.selectAllDevice();
    }

    @Override
    public Device selectById(Integer id) {
        return deviceMapper.selectById(id);
    }

    @Override
    public Device selectByIdAndPassword(Device device) {
        return deviceMapper.selectByIdAndPassword(device);
    }

    @Override
    public boolean insert(Device device) {
        device.setAddTime(new Date());
        device.setBindState(0);
        device.setInLineState(0);
        return deviceMapper.insert(device);
    }

    @Override
    public boolean delete(Device device) {
        return deviceMapper.delete(device);
    }

    @Override
    public boolean bind(Device device) {
        if (device.getId() == null || device.getPassword() == null){
            return false;
        }
        Device device1 = selectByIdAndPassword(device);
        if(device1 == null || device1.getBindState() == 1){
            return false;
        }
        device.setBindState(1);
        device.setBindTime(new Date());
        return deviceMapper.update(device);
    }

    @Autowired
    ModelService modelService;
    @Autowired
    FeignRoomClient roomClient;

    private static HashMap<Integer, Room> roomMap = new HashMap<>();
    private static HashMap<Integer, Model> modelMap = new HashMap<>();

    @Override
    public List<Device> selectByUserId(User user) {
        List<Device> devices = deviceMapper.selectByUserId(user);
        for (Device device : devices) {
            if(modelMap.containsKey(device.getModelId())){
                device.setModel(modelMap.get(device.getModelId()));
            }else{
                Model model = modelService.selectById(device.getModelId());
                device.setModel(model);
                modelMap.put(model.getId(), model);
            }

            if(roomMap.containsKey(device.getRoomId())){
                device.setRoom(roomMap.get(device.getRoomId()));
            }else{
                Room room = roomClient.getByIdFeign(device.getRoomId());
                device.setRoom(room);
                roomMap.put(device.getRoomId(), room);
            }
            String s = redisTemplate.opsForValue().get("device:" + device.getId());
            if(s != null){
                device.setInLineState(1);
                device.setJsonStatusInfo(s);
            }else{
                device.setInLineState(0);
            }
        }
        return devices;
    }

    @Override
    public boolean updateRoom(Device device) {
        return deviceMapper.updateRoom(device);
    }

    @Override
    public boolean updateTitle(Device device) {
        return deviceMapper.updateTitle(device);
    }

}
