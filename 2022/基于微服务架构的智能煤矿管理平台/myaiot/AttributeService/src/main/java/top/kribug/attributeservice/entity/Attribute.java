package top.kribug.attributeservice.entity;

import lombok.Data;

@Data
public class Attribute {
    private Integer id;
    private Integer modelId;
    private String title;
    private String type;
    private String key;
}
