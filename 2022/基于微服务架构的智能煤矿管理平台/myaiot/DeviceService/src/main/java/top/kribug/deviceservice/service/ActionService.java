package top.kribug.deviceservice.service;

import org.apache.ibatis.annotations.*;
import org.springframework.stereotype.Service;
import top.kribug.deviceservice.entity.Action;
import top.kribug.deviceservice.entity.Automation;

import java.util.List;

@Service
public interface ActionService {

    List<Action> selectAllAction();

    Action selectById(Integer id);

    List<Action> selectByAutomationId(Automation automation);

    boolean insert(Action action);

    boolean delete(Action action);

    boolean update(Action action);
}
