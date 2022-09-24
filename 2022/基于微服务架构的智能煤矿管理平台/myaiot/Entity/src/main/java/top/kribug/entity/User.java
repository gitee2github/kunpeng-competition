package top.kribug.entity;

import lombok.Data;

import java.util.Date;

@Data
public class User {
    private Integer id;
    private String username;
    private String password;
    private String phone;
    private String name;
    private String email;
    private String headUrl;
    private Date addTime;
    private Integer state;
}
