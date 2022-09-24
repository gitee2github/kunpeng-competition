package top.kribug.userservice.result;

import lombok.Data;

@Data
public class Result<E>{
     Integer statusCode;
     E data;
     String info;

    public Result(Integer statusCode, E data) {
        this.statusCode = statusCode;
        this.data = data;
    }

    public Result(Integer statusCode, E data, String info) {
        this.statusCode = statusCode;
        this.data = data;
        this.info = info;
    }
}
