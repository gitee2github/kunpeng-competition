package top.kribug.optionservice.service;

import org.springframework.stereotype.Service;
import top.kribug.optionservice.entity.Option;

import java.util.List;

@Service
public interface OptionService {
    List<Option> selectAllOption();

    List<Option> selectByModelId(Integer modelId);

    Option selectById(Integer id);

    boolean insert(Option option);

    boolean delete(Option option);
}
