package top.kribug.deviceservice.service.impl;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import top.kribug.deviceservice.entity.Statistics;
import top.kribug.deviceservice.mapper.StatisticsMapper;
import top.kribug.deviceservice.service.StatisticsService;

import java.util.Date;


@Service
public class StatisticsServiceImpl implements StatisticsService {


    @Autowired
    private StatisticsMapper statisticsMapper;

    @Override
    public Boolean insert(Statistics statistics) {
        statistics.setStatus(1);
        statistics.setCreate_time(new Date());
        statistics.setUpdate_time(new Date());
        return statisticsMapper.insert(statistics);
    }
}
