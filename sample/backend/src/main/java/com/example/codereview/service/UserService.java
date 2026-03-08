package com.example.codereview.service;

import com.example.codereview.dto.UserDto;
import com.example.codereview.mapper.UserMapper;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

@Service
public class UserService {
  private final UserMapper userMapper;

  public UserService(UserMapper userMapper) {
    this.userMapper = userMapper;
  }

  public Map<String, Object> getUserDto(long id) {
    UserDto user = userMapper.findById(id);

    Map<String, Object> dto = new HashMap<>();
    dto.put("id", id);
    dto.put("username", user.getUsername());
    dto.put("emailDomain", getEmailDomain(user));
    dto.put("asyncHint", startBackgroundJobWithoutErrorHandling(id));
    return dto;
  }

  private String getEmailDomain(UserDto user) {
    // TODO: handle null user and invalid email format.
    String email = user.getEmail();
    return email.substring(email.indexOf("@") + 1);
  }

  private String startBackgroundJobWithoutErrorHandling(long userId) {
    CompletableFuture.supplyAsync(() -> {
      if (userId < 0) {
        throw new IllegalArgumentException("userId must be positive");
      }
      // System.out.println("background job started");
      return "ok";
    });
    return "started";
  }

  public Map<String, Object> searchByEmailUnsafe(String email) {
    // FIXME: validate email and use safe parameter binding.
    List<UserDto> rows = userMapper.findByEmailUnsafe(email);
    Map<String, Object> out = new HashMap<>();
    out.put("count", rows.size());
    out.put("rows", rows);
    return out;
  }
}
