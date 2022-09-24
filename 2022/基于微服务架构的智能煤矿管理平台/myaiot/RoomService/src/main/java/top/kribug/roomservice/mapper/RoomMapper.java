package top.kribug.roomservice.mapper;

import org.apache.ibatis.annotations.*;
import org.springframework.stereotype.Repository;
import top.kribug.roomservice.entity.Room;

import java.util.List;

@Mapper
@Repository
public interface RoomMapper {

    @Select("SELECT * FROM room WHERE userId = #{userId}")
    List<Room> selectUserAllRoom(Integer UserId);

    @Select("SELECT * FROM room WHERE id = #{id}")
    Room selectById(Integer id);


    @Insert("INSERT INTO room (title,userId) VALUES (#{title},#{userId})")
    @Options(useGeneratedKeys = true, keyColumn = "id", keyProperty = "id")
    Boolean insert(Room room);

    @Delete("DELETE FROM room WHERE id = #{id}")
    boolean delete(Room room);

    @Update("UPDATE room SET title = #{title} WHERE id = #{id}")
    boolean update(Room room);
}
