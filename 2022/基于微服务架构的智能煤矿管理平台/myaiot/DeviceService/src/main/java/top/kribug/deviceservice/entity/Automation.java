package top.kribug.deviceservice.entity;

import lombok.Data;

import java.util.List;
import java.util.Objects;

@Data
public class Automation {
    private Integer id;
    private Integer andCondition; //0或1，0为满足任意条件执行，1为满足所有条件执行
    private String title;
    private Integer userId;
    private Integer status;

    private User user;

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Automation)) return false;
        Automation that = (Automation) o;
        return Objects.equals(id, that.id);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }
}
