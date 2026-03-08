package com.example.codereview.mapper;

import com.example.codereview.dto.UserDto;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;

import java.util.List;

@Mapper
public interface UserMapper {
  @Select("SELECT id, username, email FROM users WHERE id = #{id}")
  UserDto findById(long id);

  @Select("SELECT id, user_name AS username, email FROM users WHERE email = '${email}'")
  List<UserDto> findByEmailUnsafe(String email);
}

