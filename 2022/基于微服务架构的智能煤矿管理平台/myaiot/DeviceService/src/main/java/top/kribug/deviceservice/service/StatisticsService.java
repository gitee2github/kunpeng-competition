package top.kribug.deviceservice.service;


import org.springframework.stereotype.Service;
import top.kribug.deviceservice.entity.Statistics;

@Service
public interface StatisticsService {

    Boolean insert(Statistics statistics);


}
