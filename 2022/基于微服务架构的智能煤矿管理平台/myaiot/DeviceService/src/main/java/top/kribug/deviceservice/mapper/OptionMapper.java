package top.kribug.deviceservice.mapper;

import org.apache.ibatis.annotations.*;
import org.springframework.stereotype.Repository;
import top.kribug.deviceservice.entity.Option;

import java.util.List;

@Mapper
@Repository
public interface OptionMapper {

    @Select("SELECT * FROM `option`")
    List<Option> selectAllOption();

    @Select("SELECT * FROM `option` WHERE id = #{id}")
    Option selectById(Integer id);

    @Select("SELECT * FROM `option` WHERE modelId = #{modelId}")
    List<Option> selectByModelId(Integer modelId);

    @Insert("INSERT INTO `option` (modelId,key,type,title,value) VALUES " +
            "(#{modelId},#{key},#{type},#{title},#{value})")
    @Options(useGeneratedKeys = true, keyColumn = "id", keyProperty = "id")
    boolean insert(Option option);

    @Delete("DELETE FROM `option` WHERE id = #{id}")
    boolean delete(Option option);

}
