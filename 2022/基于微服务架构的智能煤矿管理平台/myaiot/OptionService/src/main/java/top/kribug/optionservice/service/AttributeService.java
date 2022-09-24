package top.kribug.optionservice.service;

import org.springframework.stereotype.Service;
import top.kribug.optionservice.entity.Attribute;

import java.util.List;

@Service
public interface AttributeService {
    List<Attribute> selectAllAttribute();

    List<Attribute> selectByModelId(Integer modelId);

    Attribute selectById(Integer id);

    boolean insert(Attribute attribute);

    boolean delete(Attribute attribute);
}
