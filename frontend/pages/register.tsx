import { FormEvent, useState } from "react";
import { useRouter } from "next/router";

import Layout from "../src/components/Layout";
import { register } from "../src/api/api";
import { useAuth } from "../src/hooks/useAuth";

type FormErrors = {
  username?: string;
  email?: string;
  phone_number?: string;
  password?: string;
  confirmPassword?: string;
  general?: string;
};

function validateEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function getApiErrorMessage(error: any): string {
  const data = error?.data;

  if (!data) {
    return "Unable to connect to the server.";
  }

  if (typeof data === "string") {
    return data;
  }

  if (typeof data === "object") {
    const messages: string[] = [];

    for (const [field, value] of Object.entries(data)) {
      if (Array.isArray(value)) {
        messages.push(
          `${field}: ${value.join(", ")}`
        );
      } else if (typeof value === "string") {
        messages.push(
          `${field}: ${value}`
        );
      }
    }

    if (messages.length > 0) {
      return messages.join(" ");
    }

    if (typeof data.detail === "string") {
      return data.detail;
    }

    if (typeof data.error === "string") {
      return data.error;
    }
  }

  return "Registration failed.";
}

export default function Register() {
  const router = useRouter();
  const { setToken } = useAuth();

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [errors, setErrors] = useState<FormErrors>({});
  const [loading, setLoading] = useState(false);

  const validateForm = (): boolean => {
    const nextErrors: FormErrors = {};

    const cleanUsername = username.trim();
    const cleanEmail = email.trim();

    if (!cleanUsername) {
      nextErrors.username = "Username is required.";
    } else if (cleanUsername.length < 3) {
      nextErrors.username =
        "Username must contain at least 3 characters.";
    }

    if (!cleanEmail) {
      nextErrors.email = "Email is required.";
    } else if (!validateEmail(cleanEmail)) {
      nextErrors.email =
        "Enter a valid email address.";
    }

    if (phoneNumber.trim()) {
      const cleanPhone = phoneNumber.trim();

      if (!/^\+?[0-9]{7,15}$/.test(cleanPhone)) {
        nextErrors.phone_number =
          "Enter a valid phone number.";
      }
    }

    if (!password) {
      nextErrors.password = "Password is required.";
    } else if (password.length < 8) {
      nextErrors.password =
        "Password must contain at least 8 characters.";
    }

    if (!confirmPassword) {
      nextErrors.confirmPassword =
        "Please confirm your password.";
    } else if (password !== confirmPassword) {
      nextErrors.confirmPassword =
        "Passwords do not match.";
    }

    setErrors(nextErrors);

    return Object.keys(nextErrors).length === 0;
  };

  const submit = async (
    event: FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();

    setErrors({});

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      const response = await register({
        username: username.trim(),
        email: email.trim().toLowerCase(),
        password,
        phone_number: phoneNumber.trim() || undefined,
      });

      if (!response?.access) {
        throw new Error(
          "Registration succeeded but no access token was returned."
        );
      }

      setToken(response.access);

      await router.push("/dashboard");
    } catch (error: any) {
      setErrors({
        general: getApiErrorMessage(error),
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="min-h-[80vh] flex items-center justify-center px-4 py-10">
        <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">

          <div className="mb-8">
            <p className="mb-2 text-sm font-medium text-indigo-600">
              IdentityAI
            </p>

            <h1 className="text-3xl font-bold text-slate-900">
              Create your account
            </h1>

            <p className="mt-2 text-sm text-slate-500">
              Start building your verified digital identity.
            </p>
          </div>

          {errors.general && (
            <div className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
              <div className="font-semibold">
                We couldn&apos;t create your account.
              </div>

              <div className="mt-1">
                {errors.general}
              </div>
            </div>
          )}

          <form
            onSubmit={submit}
            className="space-y-5"
            noValidate
          >
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">
                Username
              </label>

              <input
                type="text"
                value={username}
                onChange={(event) =>
                  setUsername(event.target.value)
                }
                placeholder="starhang"
                autoComplete="username"
                disabled={loading}
                className={`w-full rounded-lg border px-4 py-3 outline-none transition ${
                  errors.username
                    ? "border-red-400 focus:ring-2 focus:ring-red-100"
                    : "border-slate-300 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
                }`}
              />

              {errors.username && (
                <p className="mt-1 text-sm text-red-600">
                  {errors.username}
                </p>
              )}
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">
                Email address
              </label>

              <input
                type="email"
                value={email}
                onChange={(event) =>
                  setEmail(event.target.value)
                }
                placeholder="you@example.com"
                autoComplete="email"
                disabled={loading}
                className={`w-full rounded-lg border px-4 py-3 outline-none transition ${
                  errors.email
                    ? "border-red-400 focus:ring-2 focus:ring-red-100"
                    : "border-slate-300 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
                }`}
              />

              {errors.email && (
                <p className="mt-1 text-sm text-red-600">
                  {errors.email}
                </p>
              )}
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">
                Phone number
                <span className="ml-1 text-slate-400">
                  (optional)
                </span>
              </label>

              <input
                type="tel"
                value={phoneNumber}
                onChange={(event) =>
                  setPhoneNumber(event.target.value)
                }
                placeholder="+977 98XXXXXXXX"
                autoComplete="tel"
                disabled={loading}
                className={`w-full rounded-lg border px-4 py-3 outline-none transition ${
                  errors.phone_number
                    ? "border-red-400 focus:ring-2 focus:ring-red-100"
                    : "border-slate-300 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
                }`}
              />

              {errors.phone_number && (
                <p className="mt-1 text-sm text-red-600">
                  {errors.phone_number}
                </p>
              )}
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">
                Password
              </label>

              <input
                type="password"
                value={password}
                onChange={(event) =>
                  setPassword(event.target.value)
                }
                placeholder="At least 8 characters"
                autoComplete="new-password"
                disabled={loading}
                className={`w-full rounded-lg border px-4 py-3 outline-none transition ${
                  errors.password
                    ? "border-red-400 focus:ring-2 focus:ring-red-100"
                    : "border-slate-300 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
                }`}
              />

              {errors.password && (
                <p className="mt-1 text-sm text-red-600">
                  {errors.password}
                </p>
              )}
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">
                Confirm password
              </label>

              <input
                type="password"
                value={confirmPassword}
                onChange={(event) =>
                  setConfirmPassword(event.target.value)
                }
                placeholder="Repeat your password"
                autoComplete="new-password"
                disabled={loading}
                className={`w-full rounded-lg border px-4 py-3 outline-none transition ${
                  errors.confirmPassword
                    ? "border-red-400 focus:ring-2 focus:ring-red-100"
                    : "border-slate-300 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
                }`}
              />

              {errors.confirmPassword && (
                <p className="mt-1 text-sm text-red-600">
                  {errors.confirmPassword}
                </p>
              )}
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-lg bg-indigo-600 px-4 py-3 font-medium text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading
                ? "Creating account..."
                : "Create account"}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-slate-500">
            Already have an account?{" "}
            <button
              type="button"
              onClick={() => router.push("/login")}
              className="font-medium text-indigo-600 hover:text-indigo-700"
            >
              Sign in
            </button>
          </p>
        </div>
      </div>
    </Layout>
  );
}
