package top.kribug.deviceservice.service;

import org.apache.ibatis.annotations.*;
import top.kribug.deviceservice.entity.Model;

import java.util.List;

public interface ModelService {

    List<Model> selectAllModel();

    Model selectById(Integer id);

    boolean insert(Model model);

    boolean delete(Model model);

    boolean update(Model model);
}
