package com.example.codereview.controller;

import com.example.codereview.service.UserService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
public class UserController {
  private final UserService userService;

  public UserController(UserService userService) {
    this.userService = userService;
  }

  @GetMapping("/api/users/{id}")
  public Map<String, Object> getUser(@PathVariable("id") long id) {
    // TODO: return stable error response on invalid id or empty result.
    System.out.println("DEBUG: getUser called with id=" + id);
    return userService.getUserDto(id);
  }

  @GetMapping("/api/users/search")
  public Map<String, Object> searchByEmail(@RequestParam("email") String email) {
    // FIXME: use safe SQL binding.
    return userService.searchByEmailUnsafe(email);
  }
}
