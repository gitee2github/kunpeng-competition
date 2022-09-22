package top.kribug.statusdataservice.service;

import org.apache.ibatis.annotations.*;
import top.kribug.statusdataservice.entity.Status;
import top.kribug.statusdataservice.vo.StatusVO;

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
