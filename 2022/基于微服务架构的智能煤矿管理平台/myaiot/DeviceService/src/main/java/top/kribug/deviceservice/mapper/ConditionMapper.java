package top.kribug.deviceservice.mapper;

import org.apache.ibatis.annotations.*;
import org.springframework.stereotype.Repository;
import top.kribug.deviceservice.entity.Automation;
import top.kribug.deviceservice.entity.Condition;
import top.kribug.deviceservice.entity.Device;

import java.util.List;

@Mapper
@Repository
public interface ConditionMapper {
    @Select("SELECT * FROM `condition`")
    List<Condition> selectAllCondition();

    @Select("SELECT * FROM `condition` WHERE id = #{id}")
    Condition selectById(Integer id);

    @Select("SELECT * FROM `condition` WHERE automationId = #{id}")
    List<Condition> selectByAutomationId(Automation automation);

    @Select("SELECT * FROM `condition` WHERE deviceId = #{id}")
    List<Condition> selectByDeviceId(Device device);

    @Insert("INSERT INTO `condition` (automationId, deviceId,attributeId,compare,value) VALUES " +
            "(#{automationId}, #{deviceId},#{attributeId},#{compare},#{value})")
    @Options(useGeneratedKeys = true, keyColumn = "id", keyProperty = "id")
    boolean insert(Condition condition);

    @Delete("DELETE FROM `condition` WHERE id = #{id}")
    boolean delete(Condition condition);

    @Update("UPDATE `condition` SET automationId = #{automationId}, deviceId = #{deviceId}, attributeId = #{attributeId}," +
            "compare = #{compare},value = #{value},  " +
            "WHERE id = #{id}")
    boolean update(Condition condition);

}
