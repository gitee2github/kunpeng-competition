package top.kribug.deviceservice.mapper;

import org.apache.ibatis.annotations.*;
import org.springframework.stereotype.Repository;
import top.kribug.deviceservice.entity.Automation;
import top.kribug.deviceservice.entity.User;

import java.util.List;

@Mapper
@Repository
public interface AutomationMapper {
    @Select("SELECT * FROM automation")
    List<Automation> selectAllAutomation();

    @Select("SELECT * FROM automation WHERE id = #{id}")
    Automation selectById(Integer id);

    @Select("SELECT * FROM automation WHERE userId = #{id}")
    List<Automation> selectByUserId(User user);

    @Insert("INSERT INTO automation (title,andCondition,userId,status) VALUES " +
            "(#{title},#{andCondition},#{userId},#{status})")
    @Options(useGeneratedKeys = true, keyColumn = "id", keyProperty = "id")
    boolean insert(Automation automation);

    @Delete("DELETE FROM automation WHERE id = #{id}")
    boolean delete(Automation automation);

    @Update("UPDATE automation SET title = #{title}, andCondition = #{andCondition}," +
            "userId = #{userId},status = #{status},  " +
            "WHERE id = #{id}")
    boolean update(Automation automation);

    @Update("UPDATE automation SET status = #{status} WHERE id = #{id}")
    boolean updateStatus(Automation automation);

    @Update("UPDATE automation SET title = #{title} WHERE id = #{id}")
    boolean updateTitle(Automation automation);
}
