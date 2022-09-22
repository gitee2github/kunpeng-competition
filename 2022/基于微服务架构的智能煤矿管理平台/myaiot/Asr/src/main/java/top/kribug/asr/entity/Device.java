package top.kribug.asr.entity;

import lombok.Data;

import java.util.Date;

@Data
public class Device {
    private Integer id;
    private Integer modelId;
    private String title;
    private String password;
    private Integer bindState;
    private Integer userId;
    private Date addTime;
    private Date bindTime;
    private Integer roomId;
    private Integer inLineState;   //是否在线
    private String jsonStatusInfo;
}
