package top.kribug.deviceservice.service.impl;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import top.kribug.deviceservice.entity.Status;
import top.kribug.deviceservice.mapper.StatusMapper;
import top.kribug.deviceservice.service.StatusService;
import top.kribug.deviceservice.vo.StatusVO;

import java.util.Date;
import java.util.List;


@Service
public class StatusServiceImpl implements StatusService {
    @Autowired
    private StatusMapper statusMapper;

    @Override
    public List<Status> selectUserAllStatus(Integer userId) {
        return statusMapper.selectUserAllStatus(userId);
    }

    @Override
    public Status selectById(Integer id) {
        return statusMapper.selectById(id);
    }

    @Override
    public Boolean insert(Status status) {
        status.setAddTime(new Date());
        return statusMapper.insert(status);
    }

    @Override
    public boolean delete(Status status) {
        return statusMapper.delete(status);
    }

    @Override
    public boolean update(Status status) {
        return statusMapper.update(status);
    }

    @Override
    public List<Status> selectByDeviceId(Integer deviceId) {
        return statusMapper.selectByDeviceId(deviceId);
    }

    @Override
    public List<Status> selectByDeviceIdAfterDate(StatusVO statusVO) {
        return statusMapper.selectByDeviceIdAfterDate(statusVO);
    }
}
