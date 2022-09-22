package top.kribug.statusdataservice.mapper;

import org.apache.ibatis.annotations.*;
import org.springframework.stereotype.Repository;
import top.kribug.statusdataservice.entity.Status;
import top.kribug.statusdataservice.vo.StatusVO;

import java.util.Date;
import java.util.HashMap;
import java.util.List;

@Mapper
@Repository
public interface StatusMapper {

    @Select("SELECT * FROM status WHERE userId = #{userId}")
    List<Status> selectUserAllStatus(Integer userId);

    @Select("SELECT * FROM status WHERE id = #{id}")
    Status selectById(Integer id);

    @Insert("INSERT INTO status (`key`,`value`,deviceId,addTime) VALUES (#{key},#{value},#{deviceId},#{addTime})")
    @Options(useGeneratedKeys = true, keyColumn = "id", keyProperty = "id")
    Boolean insert(Status status);

    @Delete("DELETE FROM status WHERE id = #{id}")
    boolean delete(Status status);

    @Update("UPDATE status SET title = #{title} WHERE id = #{id}")
    boolean update(Status status);

    @Select("SELECT * FROM status WHERE deviceId = #{deviceId}")
    List<Status> selectByDeviceId(Integer deviceId);

    @Select("SELECT * FROM status WHERE deviceId = #{deviceId} AND addTime > #{date}")
    List<Status> selectByDeviceIdAfterDate(StatusVO statusVO);
}
