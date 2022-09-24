package top.kribug.deviceservice.mapper;

import org.apache.ibatis.annotations.*;
import org.springframework.stereotype.Repository;
import top.kribug.deviceservice.entity.Action;
import top.kribug.deviceservice.entity.Automation;

import java.util.List;

@Mapper
@Repository
public interface ActionMapper {
    @Select("SELECT * FROM action")
    List<Action> selectAllAction();

    @Select("SELECT * FROM action WHERE id = #{id}")
    Action selectById(Integer id);

    @Select("SELECT * FROM action WHERE automationId = #{id}")
    List<Action> selectByAutomationId(Automation automation);

    @Insert("INSERT INTO action (deviceId,automationId,optionId) VALUES " +
            "(#{deviceId},#{automationId},#{optionId})")
    @Options(useGeneratedKeys = true, keyColumn = "id", keyProperty = "id")
    boolean insert(Action action);

    @Delete("DELETE FROM action WHERE id = #{id}")
    boolean delete(Action action);

    @Update("UPDATE action SET deviceId = #{deviceId}, automationId = #{automationId}," +
            "optionId = #{optionId}, WHERE id = #{id}")
    boolean update(Action action);
}
