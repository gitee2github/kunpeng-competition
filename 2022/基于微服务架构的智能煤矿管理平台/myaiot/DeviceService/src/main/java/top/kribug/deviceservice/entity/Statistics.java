package top.kribug.deviceservice.entity;

import java.util.Date;

public class Statistics {
    private Integer id;
    private Date update_time;
    private Date create_time;
    private String remark;
    private Integer status;
    private Integer chartType;
    private String indicative_value1;
    private String indicative_value2;
    private String indicative_value3;
    private String indicative_value4;
    private String indicative_value5;
    private String index_value;
    private String name;
    private String category;
    private String  map;
    private Double longitude;
    private Double latitude;

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public Date getUpdate_time() {
        return update_time;
    }

    public void setUpdate_time(Date update_time) {
        this.update_time = update_time;
    }

    public Date getCreate_time() {
        return create_time;
    }

    public void setCreate_time(Date create_time) {
        this.create_time = create_time;
    }

    public String getRemark() {
        return remark;
    }

    public void setRemark(String remark) {
        this.remark = remark;
    }

    public Integer getStatus() {
        return status;
    }

    public void setStatus(Integer status) {
        this.status = status;
    }

    public Integer getChartType() {
        return chartType;
    }

    public void setChartType(Integer chartType) {
        this.chartType = chartType;
    }

    public String getIndicative_value1() {
        return indicative_value1;
    }

    public void setIndicative_value1(String indicative_value1) {
        this.indicative_value1 = indicative_value1;
    }

    public String getIndicative_value2() {
        return indicative_value2;
    }

    public void setIndicative_value2(String indicative_value2) {
        this.indicative_value2 = indicative_value2;
    }

    public String getIndicative_value3() {
        return indicative_value3;
    }

    public void setIndicative_value3(String indicative_value3) {
        this.indicative_value3 = indicative_value3;
    }

    public String getIndicative_value4() {
        return indicative_value4;
    }

    public void setIndicative_value4(String indicative_value4) {
        this.indicative_value4 = indicative_value4;
    }

    public String getIndicative_value5() {
        return indicative_value5;
    }

    public void setIndicative_value5(String indicative_value5) {
        this.indicative_value5 = indicative_value5;
    }

    public String getIndex_value() {
        return index_value;
    }

    public void setIndex_value(String index_value) {
        this.index_value = index_value;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getCategory() {
        return category;
    }

    public void setCategory(String category) {
        this.category = category;
    }

    public String getMap() {
        return map;
    }

    public void setMap(String map) {
        this.map = map;
    }

    public Double getLongitude() {
        return longitude;
    }

    public void setLongitude(Double longitude) {
        this.longitude = longitude;
    }

    public Double getLatitude() {
        return latitude;
    }

    public void setLatitude(Double latitude) {
        this.latitude = latitude;
    }
}
