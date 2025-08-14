'use client'; // Required for interactivity

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';

export default function LoginPage() {
  const router = useRouter();
  const [mobile, setMobile] = useState('');
  const [code, setCode] = useState('');
  const [step, setStep] = useState(1); // 1: mobile, 2: code
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Handle sending OTP
  const handleSendCode = async () => {
    if (!/^09\d{9}$/.test(mobile)) {
      setError('شماره موبایل باید با ۰۹ شروع شود');
      return;
    }

    setLoading(true);
    try {
      await axios.post('http://localhost:8000/api/accounts/otp/send/', { phone: mobile });
      setStep(2);
      setError('');
    } catch (err) {
      setError('خطا در ارسال کد تأیید');
    } finally {
      setLoading(false);
    }
  };

  // Handle login
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (code.length !== 6) {
      setError('کد تأیید باید ۶ رقم باشد');
      return;
    }

    setLoading(true);
    try {
      const { data } = await axios.post('http://localhost:8000/api/accounts/login/', {
        phone: mobile,
        otp: code
      });
      router.push('/profile');
    } catch (err) {
      setError('کد تأیید نامعتبر است');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-50 min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-white rounded-lg shadow-lg overflow-hidden">
        {/* Logo Section */}
        <div className="bg-[#4F46E5] p-6 flex justify-center">
          <div className="w-24 h-24 bg-white rounded-full flex items-center justify-center shadow-md">
            <i className="fas fa-mobile-alt text-[#4F46E5] text-4xl"></i>
          </div>
        </div>

        {/* Form Section */}
        <div className="p-6">
          <h1 className="text-2xl font-bold text-gray-800 text-center mb-6">ورود به حساب کاربری</h1>
          
          {error && (
            <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md">
              {error}
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            {/* Mobile Number Input */}
            <div className={step === 1 ? 'block' : 'hidden'}>
              <label htmlFor="mobile" className="block text-sm font-medium text-gray-700 mb-1">
                شماره موبایل
              </label>
              <div className="relative">
                <input
                  type="tel"
                  id="mobile"
                  value={mobile}
                  onChange={(e) => setMobile(e.target.value.replace(/[^0-9]/g, ''))}
                  placeholder="09123456789"
                  maxLength={11}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-[#4F46E5] focus:border-[#4F46E5] transition duration-200"
                  dir="ltr"
                />
                <div className="absolute left-3 top-2.5 text-gray-400">
                  <i className="fas fa-mobile-alt"></i>
                </div>
              </div>
            </div>
            
            {/* Verification Code Input */}
            <div className={step === 2 ? 'block' : 'hidden'}>
              <label htmlFor="verificationCode" className="block text-sm font-medium text-gray-700 mb-1">
                کد تأیید
              </label>
              <div className="relative">
                <input
                  type="number"
                  id="verificationCode"
                  value={code}
                  onChange={(e) => setCode(e.target.value.replace(/[^0-9]/g, ''))}
                  placeholder="123456"
                  maxLength={6}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-[#4F46E5] focus:border-[#4F46E5] transition duration-200"
                  dir="ltr"
                />
                <div className="absolute left-3 top-2.5 text-gray-400">
                  <i className="fas fa-key"></i>
                </div>
              </div>
            </div>
            
            {/* Action Buttons */}
            {step === 1 ? (
              <button
                type="button"
                onClick={handleSendCode}
                disabled={loading}
                className="w-full py-2 px-4 bg-[#4F46E5] hover:bg-[#4338CA] text-white font-medium rounded-md transition duration-200 flex items-center justify-center"
              >
                {loading ? (
                  <>
                    <i className="fas fa-spinner fa-spin mr-2"></i>
                    در حال ارسال کد...
                  </>
                ) : (
                  'دریافت کد تأیید'
                )}
              </button>
            ) : (
              <button
                type="submit"
                disabled={loading}
                className="w-full py-2 px-4 bg-green-600 hover:bg-green-700 text-white font-medium rounded-md transition duration-200"
              >
                {loading ? (
                  <>
                    <i className="fas fa-spinner fa-spin mr-2"></i>
                    در حال ورود...
                  </>
                ) : (
                  'ورود به حساب'
                )}
              </button>
            )}
          </form>
          
          {/* Register Link */}
          <div className="mt-6 text-center">
            <a href="/accounts/signup" className="text-[#4F46E5] hover:text-[#4338CA] text-sm font-medium">
              ثبت‌نام برای کاربران جدید
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}