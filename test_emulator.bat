@echo off
echo ============================================
echo Testing command line emulator with VFS
echo ============================================

echo.
echo 1. Test without parameters (default VFS)
python emulator.py
pause

echo.
echo 2. Test with script final_test.txt
python emulator.py --script final_test.txt --log test1.csv
echo Check file test1.csv
pause

echo.
echo 3. Test with VFS from ZIP archive
python emulator.py --vfs final_demo.zip --script final_test.txt --log test2.csv
echo Check file test2.csv
pause

echo.
echo 4. Test error handling
python emulator.py --script test_error.txt --log test3.csv
echo Script should stop on error
pause

echo.
echo 5. Test with logging only
python emulator.py --log test4.csv
echo Check file test4.csv
pause

echo.
echo ============================================
echo All tests completed. Check created files:
dir *.csv
echo ============================================
pause