package top.kribug.deviceservice.mapper;

import org.apache.ibatis.annotations.*;
import org.springframework.stereotype.Repository;
import top.kribug.deviceservice.entity.Model;

import java.util.List;

@Mapper
@Repository
public interface ModelMapper {
    @Select("SELECT * FROM model")
    List<Model> selectAllModel();

    @Select("SELECT * FROM model WHERE id = #{id}")
    Model selectById(Integer id);

    @Insert("INSERT INTO model (pictureUrl,title,serverName) VALUES (#{pictureUrl},#{title},#{serverName})")
    @Options(useGeneratedKeys = true, keyColumn = "id", keyProperty = "id")
    boolean insert(Model model);

    @Delete("DELETE FROM model WHERE id = #{id}")
    boolean delete(Model model);

    @Update("UPDATE model SET pictureUrl = #{pictureUrl}, title = #{title}, serverName = #{serverName} WHERE id = #{id}")
    boolean update(Model model);
}
