package top.kribug.asr;

import lombok.Data;

import java.util.List;

@Data
public class Res {
    private String corpus_no;
    private String err_msg;
    private Integer err_no;
    private List<String> result;
    private String sn;
}
