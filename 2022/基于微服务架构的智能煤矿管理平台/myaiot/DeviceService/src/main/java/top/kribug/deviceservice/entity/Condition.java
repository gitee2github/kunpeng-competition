package top.kribug.deviceservice.entity;

import lombok.Data;

@Data
public class Condition {
    private Integer id;
    private Integer automationId;
    private Integer deviceId;
    private Integer attributeId;
    private Integer compare;
    private String value;

    private Automation automation;
    private Device device;
    private Attribute attribute;
}
