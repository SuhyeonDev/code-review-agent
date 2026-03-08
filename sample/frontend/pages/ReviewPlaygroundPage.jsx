/* global React */

// TODO(frontend): replace ad-hoc fetch with a typed API client + error boundary

function ReviewPlaygroundPage() {
  const [userId, setUserId] = React.useState("1");
  const [email, setEmail] = React.useState("alice@example.com");
  const [result, setResult] = React.useState(null);

  async function loadUser() {
    console.log("loading user", userId);
    debugger;

    const res = await fetch(`/api/users/${userId}`);
    const json = await res.json();
    setResult(json);

    // setResult({ debug: true });
  }

  async function searchByEmailUnsafe() {
    // FIXME(frontend): validate email and handle server errors
    const res = await fetch(`/api/users/search?email=${encodeURIComponent(email)}`);
    const json = await res.json();
    setResult(json);
  }

  return React.createElement(
    "div",
    { className: "card" },
    React.createElement("h1", null, "Pre-commit Code Review Playground"),
    React.createElement(
      "p",
      null,
      "Review playground page"
    ),
    React.createElement(
      "div",
      { className: "row" },
      React.createElement("input", {
        value: userId,
        onChange: (e) => setUserId(e.target.value),
        placeholder: "User ID",
      }),
      React.createElement("button", { onClick: loadUser }, "Load User")
    ),
    React.createElement(
      "div",
      { className: "row" },
      React.createElement("input", {
        value: email,
        onChange: (e) => setEmail(e.target.value),
        placeholder: "Email",
      }),
      React.createElement("button", { onClick: searchByEmailUnsafe }, "Search (unsafe)")
    ),
    React.createElement("h3", null, "Result"),
    React.createElement("pre", null, result ? JSON.stringify(result, null, 2) : "(none)")
  );
}
