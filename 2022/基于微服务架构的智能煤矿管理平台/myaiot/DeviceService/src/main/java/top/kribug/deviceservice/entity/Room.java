package top.kribug.deviceservice.entity;

import lombok.Data;

@Data
public class Room {
    private Integer id;
    private String title;
    private Integer userId;

    private Room room;
}
