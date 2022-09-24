package top.kribug.deviceservice.entity;

import lombok.Data;

@Data
public class Option {
    private Integer id;
    private Integer modelId;
    private String key;
    private String value;
    private String title;
    private String type;

    private Model model;

}
