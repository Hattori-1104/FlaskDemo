const EMAIL_VALID_REG = /^[a-zA-Z0-9+_-]+(.[a-zA-Z0-9_+-]+)*@([a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]*\.)+[a-zA-Z]{2,}$/;

function checkUserExistence(email) {
  $.ajax({
    url: `/api/verify_email/${email}`,
    dataType: "json",
    success: function (data) {
      const available_operations = data.available_operations;
      const able_login = available_operations.login;
      const able_register = available_operations.register;
      if (able_login) setFormMode("login");
      else if (able_register) setFormMode("register");
      else setFormMode("authorized-email-error");
    },
    error: function () {
      console.error("エラーが発生しました。");
    }
  })
}

function setFormMode(mode) {
  let form_mode =
  {
    "is_username_editable": null,
    "submit_button_state": null,
    "submit_button_label": null,
    "mode": mode
  }
  switch (mode) {
    case "register":
      form_mode.is_username_editable = true;
      form_mode.submit_button_state = true;
      form_mode.submit_button_label = "新規登録";
      break;
    case "login":
      form_mode.is_username_editable = false;
      form_mode.submit_button_state = true;
      form_mode.submit_button_label = "ログイン";
      break;
    case "fetching":
      form_mode.is_username_editable = false;
      form_mode.submit_button_state = false;
      form_mode.submit_button_label = "検索中";
      break;
    case "valid-error":
      form_mode.is_username_editable = false;
      form_mode.submit_button_state = false;
      form_mode.submit_button_label = "新規登録/ログイン";
      break;
    case "authorized-email-error":
      form_mode.is_username_editable = false;
      form_mode.submit_button_state = false;
      form_mode.submit_button_label = "Googleで認証済みです";
      break;
  }
  $("#username-input").attr("disabled", !form_mode.is_username_editable);
  $("#user-verify-button").attr("disabled", !form_mode.submit_button_state);
  $("#user-verify-button").attr("value", form_mode.submit_button_label);
  $("#user-verify-button").attr("mode", form_mode.mode);
  $("#email-existance-indicator").attr("mode", form_mode.mode);

  $("#action-input").attr("value", form_mode.mode);
}

function onChange() {
  setFormMode("fetching");
  const email = $("#email-input").val();
  if (!email) { setFormMode("valid-error"); return; }
  if (EMAIL_VALID_REG.test(email)) {
    checkUserExistence(email);
  } else {
    setFormMode("valid-error")
  }
}

$(function () {
  // デフォルト
  setFormMode("valid-error");
  onChange();
  // メールアドレスの入力に伴うバリデーションを実行
  // 正しいならデータベースにアカウントの存在を確認
  $("#email-input").on("change", onChange);
});