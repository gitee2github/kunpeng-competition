package top.kribug.deviceservice.entity;

import lombok.Data;

import java.util.Date;
import java.util.Objects;

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

    private Model model;
    private Room room;

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Device)) return false;
        Device device = (Device) o;
        return id.equals(device.id);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }
}
