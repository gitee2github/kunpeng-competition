package top.kribug.deviceservice.service;

import org.apache.ibatis.annotations.*;
import org.springframework.stereotype.Service;
import top.kribug.deviceservice.entity.Automation;
import top.kribug.deviceservice.entity.User;

import java.util.List;

@Service
public interface AutomationService {
    List<Automation> selectAllAutomation();

    Automation selectById(Integer id);

    List<Automation> selectByUserId(User user);

    boolean insert(Automation automation);

    boolean delete(Automation automation);

    boolean update(Automation automation);

    boolean updateStatus(Automation automation);

    boolean updateTitle(Automation automation);
}
