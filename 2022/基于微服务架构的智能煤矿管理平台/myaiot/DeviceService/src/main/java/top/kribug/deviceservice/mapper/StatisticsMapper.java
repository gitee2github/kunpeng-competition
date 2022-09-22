package top.kribug.deviceservice.mapper;

import org.apache.ibatis.annotations.*;
import org.springframework.stereotype.Repository;
import top.kribug.deviceservice.entity.Statistics;
import top.kribug.deviceservice.entity.Status;
import top.kribug.deviceservice.vo.StatusVO;

import java.util.List;

@Mapper
@Repository
public interface StatisticsMapper {

    @Insert("INSERT INTO statistics (`update_time`,`create_time`,`remark`,`status`,chartType,indicative_value1," +
            "indicative_value2,indicative_value3,indicative_value4,indicative_value5,index_value," +
            "name,category,map,longitude,latitude) " +
            "VALUES (#{update_time},#{create_time},#{remark},#{status},#{chartType},#{indicative_value1},#{indicative_value2},#{indicative_value3},#{indicative_value4},#{indicative_value5},#{index_value},#{name},#{category},#{map},#{longitude},#{latitude})")
    @Options(useGeneratedKeys = true, keyColumn = "id", keyProperty = "id")
    Boolean insert(Statistics statistics);

}
