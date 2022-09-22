package top.kribug.deviceservice.service;

import top.kribug.deviceservice.entity.Status;
import top.kribug.deviceservice.vo.StatusVO;

import java.util.List;

public interface StatusService {

    List<Status> selectUserAllStatus(Integer userId);

    Status selectById(Integer id);

    Boolean insert(Status status);

    boolean delete(Status status);

    boolean update(Status status);

    List<Status> selectByDeviceId(Integer deviceId);

    List<Status> selectByDeviceIdAfterDate(StatusVO statusVO);

}
