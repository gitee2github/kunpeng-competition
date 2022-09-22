package top.kribug.attributeservice.mapper;

import org.apache.ibatis.annotations.*;
import org.springframework.stereotype.Repository;
import top.kribug.attributeservice.entity.Attribute;

import java.util.List;

@Mapper
@Repository
public interface AttributeMapper {

    @Select("SELECT * FROM `attribute`")
    List<Attribute> selectAllAttribute();

    @Select("SELECT * FROM `attribute` WHERE id = #{id}")
    Attribute selectById(Integer id);

    @Select("SELECT * FROM `attribute` WHERE modelId = #{modelId}")
    List<Attribute> selectByModelId(Integer modelId);

    @Insert("INSERT INTO `attribute` (modelId,key,type,title,value) VALUES " +
            "(#{modelId},#{key},#{type},#{title},#{value})")
    @Options(useGeneratedKeys = true, keyColumn = "id", keyProperty = "id")
    boolean insert(Attribute attribute);

    @Delete("DELETE FROM `attribute` WHERE id = #{id}")
    boolean delete(Attribute attribute);

}
