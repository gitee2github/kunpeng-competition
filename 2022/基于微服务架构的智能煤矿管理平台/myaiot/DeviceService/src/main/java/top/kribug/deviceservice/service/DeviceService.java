package top.kribug.deviceservice.service;

import org.apache.ibatis.annotations.*;
import top.kribug.deviceservice.entity.Device;
import top.kribug.deviceservice.entity.User;

import java.util.List;

public interface DeviceService {
    List<Device> selectAllDevice();

    Device selectById(Integer id);

    Device selectByIdAndPassword(Device device);

    boolean insert(Device device);

    boolean delete(Device device);

    boolean bind(Device device);

    List<Device> selectByUserId(User user);

    boolean updateRoom(Device device);

    boolean updateTitle(Device device);

}
