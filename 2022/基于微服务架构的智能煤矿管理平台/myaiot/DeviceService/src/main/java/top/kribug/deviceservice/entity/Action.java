package top.kribug.deviceservice.entity;

import lombok.Data;

@Data
public class Action {
    private Integer id;
    private Integer deviceId;
    private Integer automationId;
    private Integer optionId;
    private Device device;
    private Automation automation;
    private Option option;
}
