package top.kribug.statusdataservice.entity;

import lombok.Data;

import java.util.Date;

@Data
public class Status {
    private Integer id;
    private String key;
    private String value;
    private Integer userId;
    private Integer deviceId;
    private Integer modelId;
    private Date addTime;

}
