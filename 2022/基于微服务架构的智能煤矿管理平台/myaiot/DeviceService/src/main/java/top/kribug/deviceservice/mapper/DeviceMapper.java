package top.kribug.deviceservice.mapper;

import org.apache.ibatis.annotations.*;
import org.springframework.stereotype.Repository;
import top.kribug.deviceservice.entity.Device;
import top.kribug.deviceservice.entity.User;

import java.util.List;

@Mapper
@Repository
public interface DeviceMapper {
    @Select("SELECT * FROM device")
    List<Device> selectAllDevice();

    @Select("SELECT * FROM device WHERE id = #{id}")
    Device selectById(Integer id);

    @Select("SELECT * FROM device WHERE userId = #{id}")
    List<Device> selectByUserId(User user);

    @Select("SELECT * FROM device WHERE id = #{id} AND password = #{password}")
    Device selectByIdAndPassword(Device device);

    @Insert("INSERT INTO device (modelId,title,password,bindState,userId,addTime,bindTime,roomId) VALUES " +
            "(#{modelId},#{title},#{password},#{bindState},#{userId},#{addTime},#{bindTime},#{roomId})")
    @Options(useGeneratedKeys = true, keyColumn = "id", keyProperty = "id")
    boolean insert(Device device);

    @Delete("DELETE FROM device WHERE id = #{id}")
    boolean delete(Device device);

    @Update("UPDATE device SET bindState = #{bindState}, bindTime = #{bindTime} WHERE id = #{id}")
    boolean update(Device device);

    @Update("UPDATE device SET roomId = #{roomId} WHERE id = #{id}")
    boolean updateRoom(Device device);

    @Update("UPDATE device SET title = #{title} WHERE id = #{id}")
    boolean updateTitle(Device device);
}
